#!/usr/bin/env python3
"""
Thalassemia Training Script
Train thalassemia classifier for blood cell images
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, Optional, Tuple, List
import json
from PIL import Image
import numpy as np
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

from config import get_config

CONFIG = get_config()


class BloodCellDataset(torch.utils.data.Dataset):
    """Dataset for thalassemia blood cell classification"""
    
    def __init__(self, data_dir: str, transform=None, img_size: int = 128):
        self.data_dir = Path(data_dir)
        self.img_size = img_size
        self.transform = transform or self._default_transform()
        self.samples = self._load_samples()
        
        if len(self.samples) == 0:
            raise ValueError(f"No images found in {self.data_dir}")
    
    def _default_transform(self):
        return transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def _load_samples(self) -> List[Tuple[Path, int]]:
        """Load image files and labels from directory structure"""
        samples = []
        
        # Binary classification: expect data_dir/normal/ and data_dir/abnormal/
        class_mapping = {"abnormal": 0, "normal": 1}
        
        for class_name in sorted(self.data_dir.iterdir()):
            if class_name.is_dir():
                class_label = class_mapping.get(class_name.name)
                if class_label is not None:
                    # Recursively search for images
                    for img_path in class_name.rglob("*.jpg"):
                        samples.append((img_path, class_label))
                    for img_path in class_name.rglob("*.png"):
                        samples.append((img_path, class_label))
        
        print(f"Loaded {len(samples)} samples from {self.data_dir}")
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            return torch.zeros(3, self.img_size, self.img_size), label


class ThalassemiaTrainer:
    """Trainer for thalassemia classifier"""
    
    def __init__(self, config):
        self.config = config
        self.device = self._get_device()
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    def _get_device(self):
        if torch.cuda.is_available():
            print(f"Using CUDA: {torch.cuda.get_device_name()}")
            return "cuda"
        else:
            print("Using CPU - training will be slow")
            return "cpu"
    
    def _create_model(self) -> nn.Module:
        """Create EfficientNet-B0 model"""
        try:
            weights = EfficientNet_B0_Weights.DEFAULT
            model = efficientnet_b0(weights=weights)
        except:
            model = efficientnet_b0(weights=None)
        
        # Modify classifier for binary classification
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
            nn.Linear(256, self.config.num_classes)
        )
        
        return model.to(self.device)
    
    def train_epoch(self, train_loader: DataLoader) -> Tuple[float, float]:
        """Train one epoch"""
        self.model.train()
        
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(images)
            loss = nn.CrossEntropyLoss()(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            if (batch_idx + 1) % 10 == 0:
                print(f"Batch {batch_idx + 1}/{len(train_loader)} - Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate model"""
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
    
    def save_model(self, filepath: str, metrics: Dict):
        """Save model checkpoint"""
        output_dir = Path(filepath).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config.__dict__,
            'metrics': metrics,
            'model_type': 'efficientnet_b0',
            'class_mapping': {'0': 'abnormal', '1': 'normal'}
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def fit(self, train_loader: DataLoader, val_loader: DataLoader):
        """Train the model"""
        print(f"\nStarting training on {self.device}...")
        print(f"Epochs: {self.config.num_epochs}, LR: {self.config.learning_rate}")
        
        # Create model
        self.model = self._create_model()
        
        # Optimizer and scheduler
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=self.config.num_epochs
        )
        
        best_val_acc = 0
        patience_counter = 0
        
        for epoch in range(self.config.num_epochs):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch + 1}/{self.config.num_epochs}")
            print(f"{'='*60}")
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            
            # Validate
            val_metrics = self.validate(val_loader)
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_acc'].append(val_metrics['accuracy'])
            
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_metrics['loss']:.4f}, Val Acc: {val_metrics['accuracy']:.4f}")
            
            # Learning rate scheduling
            self.scheduler.step()
            
            # Save best model
            if val_metrics['accuracy'] > best_val_acc:
                best_val_acc = val_metrics['accuracy']
                patience_counter = 0
                
                model_path = Path(self.config.output_dir) / "thalassemia_model.pt"
                self.save_model(str(model_path), {
                    'train_loss': train_loss,
                    'train_acc': train_acc,
                    'val_loss': val_metrics['loss'],
                    'val_acc': val_metrics['accuracy'],
                    'epoch': epoch + 1
                })
            else:
                patience_counter += 1
                if patience_counter >= self.config.early_stopping_patience:
                    print(f"\nEarly stopping at epoch {epoch + 1}")
                    break
        
        # Save final history
        history_path = Path(self.config.output_dir) / "training_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"Training history saved to {history_path}")


def main():
    """Main training function"""
    # Create dataset
    print("Loading dataset...")
    print("Class Mapping: 0=Abnormal, 1=Normal\n")
    
    dataset = BloodCellDataset(
        CONFIG.data_dir,
        img_size=CONFIG.img_size
    )
    
    # Split dataset
    total = len(dataset)
    val_size = int(total * CONFIG.val_split)
    train_size = total - val_size
    
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=CONFIG.batch_size,
        shuffle=True,
        num_workers=CONFIG.num_workers
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=CONFIG.batch_size,
        shuffle=False,
        num_workers=CONFIG.num_workers
    )
    
    print(f"Train set: {len(train_dataset)}, Val set: {len(val_dataset)}")
    
    # Train
    trainer = ThalassemiaTrainer(CONFIG)
    trainer.fit(train_loader, val_loader)


if __name__ == "__main__":
    main()
