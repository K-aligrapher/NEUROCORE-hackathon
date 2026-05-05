# Malaria Binary Classification Training

Binary classification model for malaria detection: **Negative vs Positive** blood cells.

## Dataset Overview

- **Classes**: 2
  - **Negative**: Uninfected RBCs (parasitized: no)
  - **Positive**: Infected RBCs (parasitized: yes)
- **Format**: JPG/PNG images organized in class folders
- **Source**: NIH Malaria Dataset

## Dataset Structure

```
malaria/
├── Negative/      (Uninfected blood cells)
└── Positive/      (Parasitized blood cells)
```

## Training Pipeline

### Train Model
Train the binary classifier:

```bash
python train.py
```

**Training Configuration:**
- Model: EfficientNet-B0
- Image Size: 128x128
- Batch Size: 32
- Epochs: 50 (with early stopping)
- Learning Rate: 1e-4
- Device: Auto-detect (CUDA/MPS/CPU)

**Training Output:**
- `malaria_model.pt` - Best model checkpoint
- `training_history.json` - Training metrics (loss, accuracy)

### Class Mapping
```
Class 0 = Negative (Uninfected)
Class 1 = Positive (Parasitized)
```

## Model Checkpoint Format

The saved model includes:
```python
{
    'model_state_dict': {...},
    'optimizer_state_dict': {...},
    'config': {...},
    'metrics': {'train_loss', 'train_acc', 'val_loss', 'val_acc', 'epoch'},
    'model_type': 'efficientnet_b0',
    'class_mapping': {'0': 'negative', '1': 'positive'}
}
```

## Requirements
- PyTorch
- torchvision
- Pillow
- numpy

## Tips
- First run will download EfficientNet-B0 pretrained weights (~20MB)
- Training takes ~2-3 minutes per epoch on 8GB GPU
- Adjust `batch_size` in `config.py` if you run out of memory
- Early stopping activates after 10 epochs without improvement
- Data is already organized, no preprocessing needed
