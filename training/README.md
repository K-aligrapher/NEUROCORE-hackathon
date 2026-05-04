# LokiVision Training

Training scripts for blood disease classifiers.

## Requirements

```bash
pip install torch torchvision numpy pillow opencv-python
pip install ultralytics  # For YOLO
pip install pandas scikit-learn
```

## Quick Start

### 1. Download Models & Data

```bash
# Download pretrained YOLO
python training/download.py

# Or manually place your datasets:
data/malaria/Parasitized/*.png
data/malaria/Uninfected/*.png

data/sickle/normal/*.png
data/sickle/sickle/*.png
data/sickle/target/*.png
data/sickle/other_abnormal/*.png

data/thal/normal/*.png
data/thal/hypochromic/*.png
data/thal/target/*.png
data/thal/pencil/*.png
data/thal/microcytic/*.png
```

### 2. Train Models

```bash
# Train Malaria classifier (2 classes: parasitized, uninfected)
python training/train.py --disease malaria --data data/malaria --epochs 50 --batch 32

# Train Sickle classifier (4 classes: normal, sickle, target, other)
python training/train.py --disease sickle --data data/sickle --epochs 50 --batch 24

# Train Thalassemia classifier (5 classes)
python training/train.py --disease thal --data data/thal --epochs 50 --batch 24
```

### 3. Training Outputs

Trained models will be saved to:
- `models/malaria_classifier.pt`
- `models/sickle_classifier.pt`
- `models/thal_classifier.pt`

## Dataset Structure Expected

```
data/
├── malaria/
│   ├── Parasitized/     # Infected cells (label 0)
│   │   ├── cell001.png
│   │   └── ...
│   └── Uninfected/    # Healthy cells (label 1)
│       ├── cell001.png
│       └── ...
│
├── sickle/
│   ├── normal/           # label 0
│   ├── sickle/          # label 1
│   ├── target/          # label 2
│   └── other_abnormal/   # label 3
│
└── thal/
    ├── normal/         # label 0
    ├── hypochromic/    # label 1
    ├── target/        # label 2
    ├── pencil/       # label 3
    └── microcytic/   # label 4
```

## Training on RTX 5050 8GB

Recommended settings:
- Batch size: 32 (24 for complex models)
- Image size: 128
- Mixed precision (AMP): Enabled
- ~2-4 hours per model

## Inference

Once trained, the model will automatically be picked up by the pipeline:
```bash
# Run the API
uvicorn app.main:app --reload

# Upload blood smear image
curl -X POST http://localhost:8000/api/v1/analysis/upload \
  -F "image=@blood_smear.jpg"
```