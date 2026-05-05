"""
Thalassemia Training Configuration
Optimized for NVIDIA RTX 5050 8GB VRAM
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ThalassemiaTrainingConfig:
    """Thalassemia training configuration optimized for 8GB GPU"""
    
    # Paths - relative to this folder
    data_dir: str = "data"  # Binary classification: normal/, abnormal/
    output_dir: str = "."  # Save model in this folder
    
    # Model settings
    model_name: str = "efficientnet_b0"
    img_size: int = 128
    num_classes: int = 2  # binary: normal (0), abnormal (1)
    
    # Training settings (optimized for 8GB VRAM)
    batch_size: int = 32
    num_epochs: int = 50
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    
    # GPU settings
    device: str = "cuda"
    num_workers: int = 4
    
    # Optimizations
    use_amp: bool = True  # Mixed precision for 8GB
    use_gradient_checkpointing: bool = False
    
    # Early stopping
    early_stopping_patience: int = 10
    
    # Data split
    val_split: float = 0.15
    test_split: float = 0.15


def get_config() -> ThalassemiaTrainingConfig:
    """Get thalassemia training config"""
    return ThalassemiaTrainingConfig()
