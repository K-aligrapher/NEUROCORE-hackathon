#!/usr/bin/env python3
"""
LokiVision - Training Script
Train all 3 disease classifiers with optimal settings for 8GB VRAM
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
from datetime import datetime
import sys
import argparse
from typing import Dict, Optional
import structlog

from config import TrainingConfig, get_config
from dataset import create_dataloaders, augment_batch

logger = structlog.get_logger()


class Trainer:
    """Trainer class for disease classifiers"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = self._get_device()
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.history = {'train': [], 'val': []}
    
    def _get_device(self):
        if torch.cuda.is_available():
            logger.info(f"Using CUDA: {torch.cuda.get_device_name()}")
            return "cuda"
        elif hasattr(torch, 'mps') and torch.mps.is_available():
            logger.info("Using Apple MPS")
            return "mps"
        logger.warning("Using CPU - training will be slow")
        return "cpu"
    
    def _create_model(self, num_classes: int) -> nn.Module:
        """Create model based on config"""
        from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
        
        # Load pretrained
        try:
            weights = EfficientNet_B0_Weights.DEFAULT
            model = efficientnet_b0(weights=weights)
        except:
            model = efficientnet_b0(weights=None)
        
        # Modify classifier
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )
        
        return model.to(self.device)
    
    def train(self, train_loader: DataLoader, val_loader: Optional[DataLoader] = None):
        """Training loop"""
        
        # Setup
        self.model.train()
        scaler = torch.cuda.amp.GradScaler() if self.config.use_amp else None
        
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Apply augmentation
            images, labels = augment_batch(images, labels)
            
            self.optimizer.zero_grad()
            
            # Forward pass with AMP
            if scaler:
                with torch.cuda.amp.autocast():
                    outputs = self.model(images)
                    loss = nn.CrossEntropyLoss()(outputs, labels)
                
                scaler.scale(loss).backward()
                scaler.step(self.optimizer)
                scaler.update()
            else:
                outputs = self.model(images)
                loss = nn.CrossEntropyLoss()(outputs, labels)
                loss.backward()
                self.optimizer.step()
            
            # Metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Log progress
            if batch_idx % 10 == 0:
                logger.info(f"Batch {batch_idx}/{len(train_loader)} - Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def validate(self, val_loader: DataLoader) -> Dict:
        """Validation"""
        
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = nn.CrossEntropyLoss()(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    def save_model(self, path: Path, metrics: Dict):
        """Save model checkpoint"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics': metrics,
            'config': {
                'model_name': self.config.model_name,
                'num_classes': self.config.num_classes,
                'img_size': self.config.img_size
            }
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: Path):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"Model loaded from {path}")


def train_disease(
    disease: str,
    data_dir: str,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-4,
    output_dir: str = "models"
) -> str:
    """Train a disease classifier"""
    
    logger.info(f"Training {disease} classifier...")
    
    # Get config
    config = get_config(disease)
    config.num_epochs = epochs
    config.batch_size = batch_size
    config.learning_rate = lr
    config.output_dir = output_dir
    
    # Create dataloaders
    logger.info(f"Loading data from {data_dir}...")
    dataloaders = create_dataloaders(
        data_dir,
        disease,
        batch_size=batch_size,
        num_workers=config.num_workers
    )
    
    if not dataloaders:
        raise ValueError("No data found!")
    
    # Create trainer
    trainer = Trainer(config)
    trainer.model = trainer._create_model(config.num_classes)
    trainer.optimizer = optim.AdamW(
        trainer.model.parameters(),
        lr=lr,
        weight_decay=config.weight_decay
    )
    trainer.scheduler = optim.lr_scheduler.CosineAnnealingLR(
        trainer.optimizer,
        T_max=epochs
    )
    
    # Training loop
    best_val_acc = 0
    patience_counter = 0
    
    for epoch in range(epochs):
        logger.info(f"\n=== Epoch {epoch+1}/{epochs} ===")
        
        # Train
        train_loss, train_acc = trainer.train(dataloaders['train'])
        
        # Validate
        if dataloaders.get('val'):
            val_metrics = trainer.validate(dataloaders['val'])
            val_loss = val_metrics['loss']
            val_acc = val_metrics['accuracy']
            
            logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                output_path = Path(output_dir) / f"{disease}_classifier.pt"
                trainer.save_model(output_path, {'val_acc': val_acc})
                patience_counter = 0
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= config.early_stopping_patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
        else:
            logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        
        trainer.scheduler.step()
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Train LokiVision classifiers")
    parser.add_argument('--disease', type=str, required=True,
                        choices=['malaria', 'sickle', 'thal'],
                        help='Disease to train')
    parser.add_argument('--data', type=str, required=True,
                        help='Path to training data')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of epochs')
    parser.add_argument('--batch', type=int, default=32,
                        help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='Learning rate')
    parser.add_argument('--output', type=str, default='models',
                        help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # Train
    model_path = train_disease(
        args.disease,
        args.data,
        args.epochs,
        args.batch,
        args.lr,
        args.output
    )
    
    logger.info(f"Training complete! Model saved to {model_path}")


if __name__ == "__main__":
    main()