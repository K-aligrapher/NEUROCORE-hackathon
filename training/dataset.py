#!/usr/bin/env python3
"""
LokiVision - Dataset Loader
Supports NIH Malaria, Chula RBC-12, BCCD datasets
"""

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
from typing import Optional, List, Dict, Tuple
import structlog

logger = structlog.get_logger()


class BloodCellDataset(Dataset):
    """Dataset for blood cell classification"""
    
    def __init__(
        self,
        data_dir: str,
        disease: str = "malaria",
        transform: Optional[transforms.Compose] = None,
        img_size: int = 128
    ):
        self.data_dir = Path(data_dir)
        self.disease = disease.lower()
        self.img_size = img_size
        self.transform = transform or self._default_transform()
        
        self.samples = self._load_samples()
        logger.info(f"Loaded {len(self.samples)} samples for {disease}")
    
    def _default_transform(self) -> transforms.Compose:
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def _load_samples(self) -> List[Tuple[Path, int]]:
        """Load dataset samples based on disease type"""
        samples = []
        
        if self.disease == "malaria":
            # NIH Malaria dataset structure
            # data_dir/Parasitized/*.jpg
            # data_dir/Uninfected/*.jpg
            for label, class_name in enumerate(['parasitized', 'uninfected']):
                class_dir = self.data_dir / class_name
                if class_dir.exists():
                    for img_path in class_dir.glob("*.jpg"):
                        samples.append((img_path, label))
                    for img_path in class_dir.glob("*.png"):
                        samples.append((img_path, label))
        
        elif self.disease == "sickle":
            # Sickle cell dataset
            for label, class_name in enumerate(['normal', 'sickle', 'target', 'other_abnormal']):
                class_dir = self.data_dir / class_name
                if class_dir.exists():
                    for img_path in class_dir.glob("*"):
                        if img_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                            samples.append((img_path, label))
        
        elif self.disease == "thal":
            # Thalassemia dataset
            for label, class_name in enumerate(['normal', 'hypochromic', 'target', 'pencil', 'microcytic']):
                class_dir = self.data_dir / class_name
                if class_dir.exists():
                    for img_path in class_dir.glob("*"):
                        if img_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                            samples.append((img_path, label))
        
        # If no samples found, try flat structure
        if not samples:
            for img_path in self.data_dir.glob("*"):
                if img_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                    # Try to infer label from folder name
                    label = self._infer_label(img_path.parent.name)
                    if label >= 0:
                        samples.append((img_path, label))
        
        return samples
    
    def _infer_label(self, name: str) -> int:
        """Infer class label from path name"""
        name = name.lower()
        
        if self.disease == "malaria":
            if 'parasit' in name or 'infec' in name:
                return 0
            elif 'uninf' in name or 'normal' in name:
                return 1
        
        elif self.disease == "sickle":
            if 'sickle' in name:
                return 1
            elif 'target' in name:
                return 2
            elif 'abnormal' in name:
                return 3
            else:
                return 0  # normal
        
        elif self.disease == "thal":
            if 'hypo' in name:
                return 1
            elif 'target' in name:
                return 2
            elif 'pencil' in name:
                return 3
            elif 'micro' in name:
                return 4
            else:
                return 0  # normal
        
        return -1
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        
        try:
            # Load image
            img = Image.open(img_path).convert('RGB')
            img = np.array(img)
            
            # Apply transform
            img = self.transform(img)
            
            return img, label
        
        except Exception as e:
            logger.warning(f"Error loading {img_path}: {e}")
            # Return a blank image
            return torch.zeros(3, self.img_size, self.img_size), label


class SmearImageDataset(Dataset):
    """Dataset for full smear images (for YOLO training)"""
    
    def __init__(
        self,
        data_dir: str,
        annotations_dir: Optional[str] = None,
        img_size: int = 640
    ):
        self.data_dir = Path(data_dir)
        self.annotations_dir = Path(annotations_dir) if annotations_dir else None
        self.img_size = img_size
        
        self.images = self._load_images()
        logger.info(f"Loaded {len(self.images)} smear images")
    
    def _load_images(self) -> List[Path]:
        images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            images.extend(self.data_dir.glob(ext))
        return images
    
    def __len__(self) -> int:
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Dict:
        img_path = self.images[idx]
        
        img = Image.open(img_path).convert('RGB')
        img = img.resize((self.img_size, self.img_size))
        img = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
        
        # Try to load annotations
        boxes = []
        labels = []
        
        if self.annotations_dir:
            annotation_path = self.annotations_dir / f"{img_path.stem}.txt"
            if annotation_path.exists():
                with open(annotation_path) as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            labels.append(int(parts[0]))
                            boxes.append([float(x) for x in parts[1:]])
        
        return {
            'image': img,
            'boxes': boxes,
            'labels': labels,
            'path': str(img_path)
        }


def create_dataloaders(
    data_dir: str,
    disease: str = "malaria",
    batch_size: int = 32,
    img_size: int = 128,
    num_workers: int = 4,
    val_split: float = 0.15,
    test_split: float = 0.15
) -> Dict[str, DataLoader]:
    """Create train/val/test dataloaders"""
    
    from torch.utils.data import random_split
    
    # Create full dataset
    dataset = BloodCellDataset(data_dir, disease, img_size=img_size)
    
    if len(dataset) == 0:
        raise ValueError(f"No samples found in {data_dir}")
    
    # Calculate split sizes
    n_samples = len(dataset)
    n_test = int(n_samples * test_split)
    n_val = int(n_samples * val_split)
    n_train = n_samples - n_test - n_val
    
    # Split dataset
    train_set, val_set, test_set = random_split(
        dataset, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Create dataloaders
    dataloaders = {
        'train': DataLoader(
            train_set,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True
        ),
        'val': DataLoader(
            val_set,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        ),
        'test': DataLoader(
            test_set,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )
    }
    
    logger.info(f"Splits: train={n_train}, val={n_val}, test={n_test}")
    
    return dataloaders


def augment_batch(images: torch.Tensor, labels: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Apply data augmentation to a batch"""
    
    batch_size = images.size(0)
    
    for i in range(batch_size):
        # Random horizontal flip
        if torch.rand(1).item() > 0.5:
            images[i] = torch.flip(images[i], dims=[2])
        
        # Random rotation (90 degree increments)
        k = torch.randint(0, 4, (1,)).item()
        if k > 0:
            images[i] = torch.rot90(images[i], k, dims=[1, 2])
        
        # Random brightness/contrast
        if torch.rand(1).item() > 0.5:
            brightness = torch.rand(1).item() * 0.4 + 0.8
            images[i] = images[i] * brightness
            images[i] = torch.clamp(images[i], 0, 1)
        
        if torch.rand(1).item() > 0.5:
            contrast = torch.rand(1).item() * 0.4 + 0.8
            mean = images[i].mean()
            images[i] = (images[i] - mean) * contrast + mean
            images[i] = torch.clamp(images[i], 0, 1)
    
    return images, labels