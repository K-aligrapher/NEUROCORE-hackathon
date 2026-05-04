"""
LokiVision - Training Configuration
Elliptocytosis instead of Thalassemia
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TrainingConfig:
    """Training configuration optimized for 8GB VRAM"""
    
    data_dir: str = "training\data"
    output_dir: str = "models"
    model_name: str = "efficientnet_b0"
    img_size: int = 128
    num_workers: int = 4
    batch_size: int = 32
    num_epochs: int = 50
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    device: str = "cuda"
    use_amp: bool = True
    early_stopping_patience: int = 10
    val_split: float = 0.15
    test_split: float = 0.15


class MalariaConfig(TrainingConfig):
    """Malaria: parasitized vs uninfected"""
    disease: str = "malaria"
    num_classes: int = 2
    class_names: list = ["parasitized", "uninfected"]


class SickleConfig(TrainingConfig):
    """Sickle Cell: normal, sickle, target, other"""
    disease: str = "sickle"
    num_classes: int = 4
    class_names: list = ["normal", "sickle", "target", "other_abnormal"]


class ElliptocytosisConfig(TrainingConfig):
    """Elliptocytosis: normal, elliptocyte, oval, pencil_cigar"""
    disease: str = "elliptocytosis"
    num_classes: int = 4
    class_names: list = ["normal", "elliptocyte", "oval", "pencil_cigar"]
    batch_size: int = 24  # Slightly smaller for shape features


def get_config(disease: str) -> TrainingConfig:
    """Get config for specific disease"""
    configs = {
        'malaria': MalariaConfig(),
        'sickle': SickleConfig(),
        'elliptocytosis': ElliptocytosisConfig(),
        'ellipt': ElliptocytosisConfig(),
    }
    
    disease_lower = disease.lower()
    if disease_lower in configs:
        return configs[disease_lower]
    
    # Try partial match
    for key, config in configs.items():
        if key in disease_lower or disease_lower in key:
            return config
    
    print(f"[WARN] Unknown disease: {disease}, using MalariaConfig")
    return MalariaConfig()


def print_config(config: TrainingConfig):
    """Print training config"""
    print("="*50)
    print("TRAINING CONFIG")
    print("="*50)
    print(f"Disease:    {config.disease}")
    print(f"Classes:    {config.num_classes}")
    print(f"Class names: {config.class_names}")
    print(f"Data dir:   {config.data_dir}")
    print(f"Output dir: {config.output_dir}")
    print(f"Batch:      {config.batch_size}")
    print(f"Epochs:     {config.num_epochs}")
    print(f"LR:         {config.learning_rate}")
    print(f"Device:     {config.device}")
    print(f"AMP:        {config.use_amp}")
    print("="*50)