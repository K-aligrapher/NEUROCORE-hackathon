# Thalassemia Binary Classification Training

Binary classification model for thalassemia detection: **Normal vs Abnormal** blood cells.

## Dataset Overview

- **Cell Types**: 9 different types (grouped into 2 classes)
  - **Normal**: Normal RBCs (1,426 samples)
  - **Abnormal**: Elliptocyte, Pencil, Teardrop, Stomatocyte, TARGETSEL, Hypochromic, SPERO bulat, Acantocyte (~5,682 samples)
- **Total Samples**: ~7,108 images
- **Format**: PNG images in zip files

## Setup & Training Pipeline

### Step 1: Preprocess Data
Extract and organize zip files into binary classification folders:

```bash
python preprocess_data.py
```

This will:
- Extract all 9 zip files
- Organize images into `data/normal/` and `data/abnormal/`
- Create `data/preprocessing_stats.json` with statistics
- Clean up temporary extraction folders

**Output Structure:**
```
data/
├── normal/           (1,426 images)
├── abnormal/         (~5,682 images)
└── preprocessing_stats.json
```

### Step 2: Train Model
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
- `thalassemia_model.pt` - Best model checkpoint
- `training_history.json` - Training metrics (loss, accuracy)

### Class Mapping
```
Class 0 = Abnormal
Class 1 = Normal
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
    'class_mapping': {'0': 'abnormal', '1': 'normal'}
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
