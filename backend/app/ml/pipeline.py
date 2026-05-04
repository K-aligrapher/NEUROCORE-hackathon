#!/usr/bin/env python3
"""
LokiVision - GPU-Optimized Blood Smear Analysis Pipeline
Malaria + Thalassemia only (with debugging)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import structlog
import time
import sys

# Console output for debugging
def DEBUG(msg: str):
    print(f"[DEBUG {time.strftime('%H:%M:%S')}] {msg}", flush=True)

def INFO(msg: str):
    print(f"[INFO {time.strftime('%H:%M:%S')}] {msg}", flush=True)

def ERROR(msg: str):
    print(f"[ERROR {time.strftime('%H:%M:%S')}] {msg}", flush=True)

def WARN(msg: str):
    print(f"[WARN {time.strftime('%H:%M:%S')}] {msg}", flush=True)


@dataclass
class InferenceConfig:
    device: str = "cuda"
    batch_size: int = 32
    img_size: int = 128
    confidence_threshold: float = 0.7
    max_cells_analysis: int = 200


class MultiDiseaseClassifier(nn.Module):
    """
    TWO DISEASE MODEL:
    1. Malaria: [parasitized, uninfected]
    2. Thalassemia: [normal, hypochromic, target, pencil, microcytic]  <-- RESTORED!
    """
    
    def __init__(self, num_classes_per_disease: List[int] = [2, 5], model_path: Optional[str] = None):
        INFO("Loading MultiDiseaseClassifier (Malaria + Thalassemia)...")
        super().__init__()
        
        # Load EfficientNet-B0
        try:
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            weights = EfficientNet_B0_Weights.DEFAULT
            self.backbone = efficientnet_b0(weights=weights)
            INFO("EfficientNet-B0 backbone loaded")
        except Exception as e:
            ERROR(f"Failed to load EfficientNet: {e}")
            raise
        
        self.feature_dim = 1280
        
        # Freeze early layers
        for i, param in enumerate(self.backbone.features[:5].parameters()):
            param.requires_grad = False
        
        # Disease-specific heads
        # Malaria: 2 classes (parasitized, uninfected)
        self.malaria_head = nn.Linear(self.feature_dim, 2)
        
        # Thalassemia: 5 classes (normal, hypochromic, target, pencil, microcytic)
        self.thal_head = nn.Linear(self.feature_dim + 5, 5)
        
        # Load trained weights
        if model_path and Path(model_path).exists():
            INFO(f"Loading weights from {model_path}")
            try:
                self.load_state_dict(torch.load(model_path, map_location='cpu'))
                INFO("Trained weights loaded!")
            except Exception as e:
                WARN(f"Could not load weights: {e}")
        else:
            WARN("NO TRAINED MODEL - using untrained model")
    
    def extract_color_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract color features for thalassemia detection"""
        DEBUG("Extracting color features for thalassemia...")
        
        batch_size = x.size(0)
        color_features = []
        
        x_np = (x.cpu().numpy().transpose(0, 2, 3, 1) * 255).astype(np.uint8)
        
        for i in range(batch_size):
            img = x_np[i]
            
            # LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            l, a, b = lab[:,:,0], lab[:,:,1], lab[:,:,2]
            
            h, w = img.shape[:2]
            center = img[h//4:3*h//4, w//4:3*w//4]
            
            # Central pallor - critical for thalassemia!
            center_mean = np.mean(center)
            overall_mean = np.mean(img)
            pallor_ratio = 1 - (center_mean / (overall_mean + 1e-6))
            
            # Color channel statistics
            l_mean = np.mean(l) / 255
            a_mean = np.mean(a) / 255
            b_mean = np.mean(b) / 255
            l_std = np.std(l) / 255
            
            features = [pallor_ratio, l_mean, a_mean, b_mean, l_std]
            color_features.append(features)
        
        DEBUG(f"Color features: {len(color_features)} samples")
        return torch.tensor(color_features, dtype=torch.float32)
    
    def forward(self, x: torch.Tensor):
        DEBUG(f"Forward pass input: {x.shape}")
        
        # Shared features
        features = self.backbone.features(x)
        features = F.adaptive_avg_pool2d(features, 1).view(features.size(0), -1)
        DEBUG(f"Features shape: {features.shape}")
        
        # Malaria (texture-based)
        malaria_logits = self.malaria_head(features)
        
        # Thalassemia (color-based)
        color_feats = self.extract_color_features(x).to(x.device)
        thal_input = torch.cat([features, color_feats], dim=1)
        thal_logits = self.thal_head(thal_input)
        
        return malaria_logits, thal_logits


class YOLOv8Detector:
    """YOLOv8 for blood cell detection"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.device = self._get_device()
        self.model = None
        self.use_yolo = False
        self._load_model()
    
    def _get_device(self):
        if torch.cuda.is_available():
            INFO(f"GPU: {torch.cuda.get_device_name()}")
            return "cuda"
        elif hasattr(torch, 'mps') and torch.mps.is_available():
            INFO("Using Apple MPS")
            return "mps"
        WARN("No GPU - using CPU")
        return "cpu"
    
    def _load_model(self):
        INFO("Loading YOLOv8...")
        
        try:
            from ultralytics import YOLO
        except ImportError:
            ERROR("Ultralytics not installed! Install: pip install ultralytics")
            self._load_fallback()
            return
        
        model_path = Path("models/yolov8n.pt")
        
        try:
            if model_path.exists():
                self.model = YOLO(str(model_path))
            else:
                INFO("Downloading YOLOv8n...")
                self.model = YOLO("yolov8n.pt")
            
            self.model.to(self.device)
            self.use_yolo = True
            INFO("YOLOv8 loaded!")
        except Exception as e:
            ERROR(f"YOLO load failed: {e}")
            self._load_fallback()
    
    def _load_fallback(self):
        WARN("Using OpenCV fallback")
        self.use_yolo = False
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        INFO(f"Detecting cells in {image.shape[:2]}...")
        t0 = time.time()
        
        if self.use_yolo and self.model:
            try:
                results = self.model(
                    image,
                    conf=self.config.confidence_threshold,
                    device=self.device,
                    verbose=False,
                    imgsz=640
                )
                
                detections = []
                for r in results:
                    for box in r.boxes:
                        detections.append({
                            'bbox': box.xyxy[0].cpu().numpy().tolist(),
                            'confidence': float(box.conf[0]),
                            'class': int(box.cls[0])
                        })
                
                INFO(f"YOLO found {len(detections)} cells in {time.time()-t0:.2f}s")
                return detections
            except Exception as e:
                ERROR(f"YOLO failed: {e}")
        
        return self._opencv_detect(image)
    
    def _opencv_detect(self, image: np.ndarray) -> List[Dict]:
        INFO("Using OpenCV detection...")
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for cnt in contours[:self.config.max_cells_analysis]:
            area = cv2.contourArea(cnt)
            if 200 < area < 8000:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    'bbox': [x, y, x+w, y+h],
                    'confidence': 0.8,
                    'class': 0
                })
        
        INFO(f"OpenCV found {len(detections)} cells")
        return detections


class OptimizedPipeline:
    """GPU-OPTIMIZED pipeline with Malaria + Thalassemia"""
    
    def __init__(self, config: Optional[InferenceConfig] = None):
        self.config = config or InferenceConfig()
        self.device = self._get_device()
        
        INFO("="*60)
        INFO("LOKIVISION PIPELINE INITIALIZATION")
        INFO("="*60)
        
        # Load detector
        INFO("[1/3] Loading YOLOv8 detector...")
        self.detector = YOLOv8Detector(self.config)
        
        # Load classifier
        INFO("[2/3] Loading disease classifier...")
        self.classifier = self._load_classifier()
        
        # Transforms
        INFO("[3/3] Setting up transforms...")
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((self.config.img_size, self.config.img_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        INFO("="*60)
        INFO(f"Pipeline ready! Device: {self.device}")
        INFO("Diseases: Malaria + Thalassemia")
        INFO("="*60)
    
    def _get_device(self):
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch, 'mps') and torch.mps.is_available():
            return "mps"
        return "cpu"
    
    def _load_classifier(self):
        model_paths = [
            "models/multi_disease_classifier.pt",
            "models/malaria_classifier.pt",
            "models/thal_classifier.pt"
        ]
        
        for path in model_paths:
            if Path(path).exists():
                INFO(f"Found: {path}")
                try:
                    return MultiDiseaseClassifier(model_path=path)
                except Exception as e:
                    ERROR(f"Load error: {e}")
        
        ERROR("NO TRAINED MODEL - using untrained")
        return MultiDiseaseClassifier()
    
    def run(self, image: np.ndarray) -> Dict:
        """Run analysis with Malaria + Thalassemia"""
        
        INFO("="*60)
        INFO("STARTING ANALYSIS")
        INFO("="*60)
        
        t_total = time.time()
        
        # Step 1: Detect
        INFO("[1/4] Detecting cells...")
        t1 = time.time()
        detections = self.detector.detect(image)
        t_detect = time.time() - t1
        
        if len(detections) < 10:
            ERROR(f"Too few cells: {len(detections)}")
            return {'status': 'failed', 'error': f'Only {len(detections)} cells'}
        
        INFO(f"  Found {len(detections)} cells in {t_detect:.2f}s")
        
        # Step 2: Crop
        INFO("[2/4] Cropping cells...")
        t2 = time.time()
        cell_tensors = []
        
        for cell in detections[:self.config.max_cells_analysis]:
            x1, y1, x2, y2 = map(int, cell['bbox'])
            
            pad = 5
            x1, y1 = max(0, x1-pad), max(0, y1-pad)
            x2, y2 = min(image.shape[1], x2+pad), min(image.shape[0], y2+pad)
            
            crop = image[y1:y2, x1:x2]
            if crop.size > 0:
                cell_tensors.append(self.transform(crop))
        
        crop_count = len(cell_tensors)
        t_crop = time.time() - t2
        INFO(f"  Cropped {crop_count} cells in {t_crop:.2f}s")
        
        if not cell_tensors:
            return {'status': 'failed', 'error': 'No valid cells'}
        
        # Step 3: Classify with GPU batch
        INFO(f"[3/4] Classifying {crop_count} cells on {self.device}...")
        t3 = time.time()
        
        batch = torch.stack(cell_tensors).to(self.device)
        DEBUG(f"  Batch: {batch.shape}")
        
        with torch.no_grad():
            mal_logits, thal_logits = self.classifier(batch)
            
            mal_preds = torch.argmax(mal_logits, dim=1)
            mal_probs = F.softmax(mal_logits, dim=1).max(dim=1)[0]
            
            thal_preds = torch.argmax(thal_logits, dim=1)
            thal_probs = F.softmax(thal_logits, dim=1).max(dim=1)[0]
        
        t_class = time.time() - t3
        INFO(f"  Classification in {t_class:.2f}s")
        
        # Step 4: Aggregate
        INFO("[4/4] Aggregating results...")
        
        cell_count = len(cell_tensors)
        
        mal_pos = int((mal_preds == 0).sum())  # parasitized
        thal_pos = int((thal_preds != 0).sum())  # abnormal thalassemia
        
        mal_rate = mal_pos / cell_count
        thal_rate = thal_pos / cell_count
        
        mal_severity = "severe" if mal_rate > 0.05 else "moderate" if mal_rate > 0.01 else "low"
        
        t_total = time.time() - t_total
        
        INFO("="*60)
        INFO("ANALYSIS COMPLETE!")
        INFO(f"Total: {t_total:.2f}s | Cells: {cell_count}")
        INFO(f"Malaria: {'+' if mal_pos > 0 else '-'} ({mal_pos}, {mal_rate*100:.1f}%)")
        INFO(f"Thalassemia: {'+' if thal_pos > 0 else '-'} ({thal_pos}, {thal_rate*100:.1f}%)")
        INFO("="*60)
        
        return {
            'status': 'completed',
            'device': self.device,
            'timing': {'detection': t_detect, 'crop': t_crop, 'classify': t_class, 'total': t_total},
            'cell_statistics': {
                'total_detected': len(detections),
                'rbc_count': cell_count,
                'wbc_count': 0,
                'platelet_count': 0,
                'rejected_count': len(detections) - cell_count
            },
            'results': {
                'malaria': {
                    'diagnosis': 'Positive' if mal_pos > 0 else 'Negative',
                    'confidence': round(float(mal_probs.mean()), 3),
                    'positive_rate': round(mal_rate, 3),
                    'positive_count': mal_pos,
                    'severity': mal_severity,
                    'cell_distribution': {'parasitized': mal_pos, 'uninfected': cell_count - mal_pos}
                },
                'thalassemia': {
                    'diagnosis': 'Positive' if thal_pos > 0 else 'Negative',
                    'confidence': round(float(thal_probs.mean()), 3),
                    'positive_rate': round(thal_rate, 3),
                    'positive_count': thal_pos,
                    'cell_distribution': {
                        'normal': cell_count - thal_pos,
                        'hypochromic': int((thal_preds == 1).sum()),
                        'target': int((thal_preds == 2).sum()),
                        'pencil': int((thal_preds == 3).sum()),
                        'microcytic': int((thal_preds == 4).sum())
                    }
                }
            },
            'quality_flags': [],
            'disclaimer': 'AI-assisted only. Not for clinical diagnosis.',
            'model_versions': {'segmentor': 'yolov8n', 'classifier': 'malaria-thal-v1'}
        }


# Singleton
pipeline = None

def get_pipeline() -> OptimizedPipeline:
    global pipeline
    if pipeline is None:
        pipeline = OptimizedPipeline()
    return pipeline