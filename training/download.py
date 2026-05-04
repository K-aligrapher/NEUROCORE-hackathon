#!/usr/bin/env python3
"""
LokiVision - Download pretrained models and datasets
"""

import urllib.request
import zipfile
import os
from pathlib import Path
import structlog

logger = structlog.get_logger()


def download_file(url: str, dest: Path):
    """Download file with progress"""
    logger.info(f"Downloading {url}...")
    
    def progress(count, block_size, total_size):
        if total_size > 0:
            percent = int(count * block_size * 100 / total_size)
            if count % 100 == 0:
                print(f"\r{percent}%", end="", flush=True)
    
    urllib.request.urlretrieve(url, dest, progress)
    print()


def download_yolov8():
    """Download YOLOv8n model"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / "yolov8n.pt"
    if model_path.exists():
        logger.info("YOLOv8 already exists")
        return
    
    # Download from Ultralytics
    url = "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt"
    try:
        download_file(url, model_path)
        logger.info(f"YOLOv8n saved to {model_path}")
    except Exception as e:
        logger.warning(f"Could not download YOLOv8: {e}")


def download_malaria_dataset():
    """Download NIH Malaria dataset"""
    data_dir = Path("data") / "malaria"
    
    if (data_dir / "Parasitized").exists():
        logger.info("Malaria dataset already exists")
        return
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Kaggle URL (need Kaggle CLI or use browser)
    logger.info("""
To download Malaria dataset:
1. Go to: https://www.kaggle.com/datasets/iarunava/cell-images-for-detecting-malaria
2. Download and extract to data/malaria/

Structure expected:
data/malaria/
  ├── Parasitized/
  │   └── *.png
  └── Uninfected/
      └── *.png
""")


def download_bccd_dataset():
    """Download BCCD dataset for cell detection"""
    data_dir = Path("data") / "bccd"
    
    if data_dir.exists():
        logger.info("BCCD dataset already exists")
        return
    
    logger.info("""
To download BCCD dataset:
1. Go to: https://github.com/Shengularity/BCCD_Dataset
2. Download and extract to data/bccd/
""")


def download_efficientnet():
    """Download EfficientNet pretrained weights (auto from torchvision)"""
    import torchvision.models as models
    
    logger.info("EfficientNet weights will be downloaded automatically by torchvision")
    
    # Test download
    try:
        weights = models.EfficientNet_B0_Weights.DEFAULT
        logger.info(f"EfficientNet-B0 available: {len(weights.meta['categories'])} categories")
    except Exception as e:
        logger.warning(f"Could not load EfficientNet: {e}")


def main():
    """Main setup function"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     LokiVision - Model & Dataset Downloader       ║
╚══════════════════════════════════════════════════╝
""")
    
    # Create directories
    Path("models").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Download models
    print("\n[1/4] Downloading YOLOv8n...")
    download_yolov8()
    
    print("\n[2/4] Checking EfficientNet...")
    download_efficientnet()
    
    print("\n[3/4] Malaria dataset info...")
    download_malaria_dataset()
    
    print("\n[4/4] BCCD dataset info...")
    download_bccd_dataset()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║  Setup Complete!                                  ║
╠══════════════════════════════════════════════════════════╣
║                                                 ║
║  Next steps:                                    ║
║                                                 ║
║  1. Download datasets:                          ║
║     malaria: kaggle.com/datasets/iarunava/       ║
║                cell-images-for-detecting-malaria ║
║                                                 ║
║  2. Place data in folders:                     ║
║     data/malaria/Parasitized/                  ║
║     data/malaria/Uninfected/                    ║
║                                                 ║
║  3. Train models:                            ║
║     python training/train.py --disease malaria     ║
║                --data data/malaria            ║
║                --epochs 50                  ║
║                                                 ║
╚══════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()