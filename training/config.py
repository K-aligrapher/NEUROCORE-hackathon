"""
LokiVision - Training Configuration
Optimized for NVIDIA RTX 5050 8GB VRAM
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TrainingConfig:
    """Training configuration optimized for 8GB GPU"""
    
    # Paths
    data_dir: str = "data"
    output_dir: str = "models"
    
    # Model settings
    model_name: str = "efficientnet_b0"
    img_size: int = 128  # Smaller for 8GB VRAM
    num_classes: int = 2
    
    # Training settings (optimized for 8GB VRAM)
    batch_size: int = 32  # 32 for 8GB
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


class MalariaConfig(TrainingConfig):
    """Malaria classification config"""
    model_name: str = "efficientnet_b0"
    num_classes: int = 2  # parasitized, uninfected
    batch_size: int = 32
    learning_rate: float = 1e-4
    

class SickleConfig(TrainingConfig):
    """Sickle cell classification config"""
    model_name: str = "mobilenet_v3_large"
    num_classes: int = 4  # normal, sickle, target, other
    batch_size: int = 24  # Smaller due to shape features
    learning_rate: float = 8e-5


class ThalConfig(TrainingConfig):
    """Thalassemia classification config"""
    model_name: str = "efficientnet_b2"
    num_classes: int = 5  # normal, hypochromic, target, pencil, microcytic
    batch_size: int = 24
    learning_rate: float = 1e-4


def get_config(disease: str) -> TrainingConfig:
    """Get config for specific disease"""
    configs = {
        'malaria': MalariaConfig(),
        'sickle': SickleConfig(),
        'thal': ThalConfig()
    }
    return configs.get(disease.lower(), MalariaConfig())