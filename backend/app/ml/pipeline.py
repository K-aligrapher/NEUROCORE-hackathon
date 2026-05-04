#!/usr/bin/env python3
"""
LokiVision - GPU-Optimized Blood Smear Analysis Pipeline
With Elliptocytosis replacement + comprehensive debugging
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

# Configure structured logging with console output for debugging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("lokivision")

# Print debug wrapper to console
def DEBUG(msg: str):
    """Print debug message to console"""
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
    SINGLE MODEL for 3 diseases:
    1. Malaria: [parasitized, uninfected]
    2. Sickle: [normal, sickle, target, other]
    3. Elliptocytosis: [normal, elliptocyte, oval, pencil/cigar]  <-- CHANGED!
    """
    
    def __init__(self, num_classes_per_disease: List[int] = [2, 4, 4], model_path: Optional[str] = None):
        INFO("Loading MultiDiseaseClassifier...")
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
        
        # Sickle: 4 classes (normal, sickle, target, other_abnormal)
        self.sickle_head = nn.Linear(self.feature_dim + 12, 4)
        
        # Elliptocytosis: 4 classes (normal, elliptocyte, oval, pencil_cigar)
        # This replaces Thalassemia detection
        self.elliptocytosis_head = nn.Linear(self.feature_dim + 8, 4)
        
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
    
    def extract_shape_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract shape features for sickle detection"""
        DEBUG("Extracting shape features...")
        
        batch_size = x.size(0)
        shape_features = []
        
        x_np = (x.cpu().numpy().transpose(0, 2, 3, 1) * 255).astype(np.uint8)
        
        for i in range(batch_size):
            img = x_np[i]
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                cnt = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True) + 1e-6
                circularity = 4 * np.pi * area / (perimeter ** 2)
                
                x, y, w, h = cv2.boundingRect(cnt)
                aspect = w / (h + 1e-6)
                
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull) + 1e-6
                solidity = area / hull_area
                
                rect_area = w * h + 1e-6
                extent = area / rect_area
                
                # Major/minor axis for elliptocyte detection
                try:
                    if len(cnt) >= 5:
                        ell = cv2.fitEllipse(cnt)
                        major_axis = max(ell[1])
                        minor_axis = min(ell[1])
                        axis_ratio = minor_axis / (major_axis + 1e-6)
                    else:
                        axis_ratio = 1.0
                except:
                    axis_ratio = 1.0
                
                features = [circularity, aspect, solidity, extent, axis_ratio, 
                          1/circularity if circularity > 0.1 else 10] + list(np.zeros(5))
            else:
                features = [0.5, 1.0, 0.5, 0.5, 1.0] + list(np.zeros(5))
            
            shape_features.append(features[:11])
        
        DEBUG(f"Shape features: {len(shape_features)} samples")
        return torch.tensor(shape_features, dtype=torch.float32)
    
    def extract_elliptocyte_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features specifically for elliptocyte/pencil/cigar detection"""
        DEBUG("Extracting elliptocyte features...")
        
        batch_size = x.size(0)
        ellipt_features = []
        
        x_np = (x.cpu().numpy().transpose(0, 2, 3, 1) * 255).astype(np.uint8)
        
        for i in range(batch_size):
            img = x_np[i]
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            features = [0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5]  # default
            
            if contours:
                cnt = max(contours, key=cv2.contourArea)
                
                # Get bounding box
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Aspect ratio - very important for elliptocytes!
                aspect_ratio = w / (h + 1e-6)
                extent_ratio = w * h / ((x_np.shape[1] * x_np.shape[0]) + 1e-6)
                
                # Perimeter
                perimeter = cv2.arcLength(cnt, True) + 1e-6
                
                # Circularity (elliptocytes have low circularity)
                area = cv2.contourArea(cnt)
                circularity = 4 * np.pi * area / (perimeter ** 2)
                
                # Try ellipse fitting
                if len(cnt) >= 5:
                    try:
                        ell = cv2.fitEllipse(cnt)
                        (cx, cy), (ma, mb), angle = ell
                        ellipticity = min(ma, mb) / (max(ma, mb) + 1e-6)  # close to 1 = circle
                        eccentricity = np.sqrt(1 - ellipticity ** 2)
                    except:
                        ellipticity = 1.0
                        eccentricity = 0.0
                else:
                    ellipticity = 1.0
                    eccentricity = 0.0
                
                # Cigar/pencil detection - very elongated with nearly parallel sides
                is_cigar = 1.0 if (aspect_ratio < 0.4 or aspect_ratio > 2.5) else 0.0
                
                # Ovals - moderately elongated
                is_oval = 1.0 if (0.4 <= aspect_ratio < 0.6 or 1.7 < aspect_ratio <= 2.5) else 0.0
                
                features = [
                    aspect_ratio,           # 1: width/height ratio
                    circularity,            # 2: how circular
                    ellipticity,            # 3: ellipse fit
                    eccentricity,          # 4: eccentricity
                    is_cigar,              # 5: cigar-shaped indicator
                    is_oval,               # 6: oval-shaped indicator
                    extent_ratio,         # 7: area in bounding box
                    1 - abs(1 - aspect_ratio)  # 8: deviation from 1
                ]
            
            ellipt_features.append(features)
        
        DEBUG(f"Elliptocyte features: {len(ellipt_features)} samples")
        return torch.tensor(ellipt_features, dtype=torch.float32)
    
    def forward(self, x: torch.Tensor):
        DEBUG(f"Forward pass input: {x.shape}")
        
        # Shared features
        features = self.backbone.features(x)
        features = F.adaptive_avg_pool2d(features, 1).view(features.size(0), -1)
        DEBUG(f"Features shape: {features.shape}")
        
        # Malaria (texture)
        malaria_logits = self.malaria_head(features)
        
        # Sickle (shape)
        shape_feats = self.extract_shape_features(x)
        sickle_input = torch.cat([features, shape_feats.to(x.device)], dim=1)
        sickle_logits = self.sickle_head(sickle_input)
        
        # Elliptocytosis (specific shape features!)
        ellipt_feats = self.extract_elliptocyte_features(x).to(x.device)
        ellipt_input = torch.cat([features, ellipt_feats], dim=1)
        ellipt_logits = self.elliptocytosis_head(ellipt_input)
        
        return malaria_logits, sickle_logits, ellipt_logits


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
    """
    GPU-OPTIMIZED pipeline with Elliptocytosis detection
    """
    
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
            "models/sickle_classifier.pt",
            "models/elliptocytosis_classifier.pt"
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
        """Run analysis with Elliptocytosis detection"""
        
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
            mal_logits, sick_logits, ellipt_logits = self.classifier(batch)
            
            mal_preds = torch.argmax(mal_logits, dim=1)
            mal_probs = F.softmax(mal_logits, dim=1).max(dim=1)[0]
            
            sick_preds = torch.argmax(sick_logits, dim=1)
            sick_probs = F.softmax(sick_logits, dim=1).max(dim=1)[0]
            
            ellipt_preds = torch.argmax(ellipt_logits, dim=1)
            ellipt_probs = F.softmax(ellipt_logits, dim=1).max(dim=1)[0]
        
        t_class = time.time() - t3
        INFO(f"  Classification in {t_class:.2f}s")
        
        # Step 4: Aggregate
        INFO("[4/4] Aggregating results...")
        
        cell_count = len(cell_tensors)
        
        mal_pos = int((mal_preds == 0).sum())  # parasitized
        sick_pos = int((sick_preds == 1).sum())  # sickle
        ellipt_pos = int((ellipt_preds != 0).sum())  # abnormal elliptocytes
        
        mal_rate = mal_pos / cell_count
        sick_rate = sick_pos / cell_count
        ellipt_rate = ellipt_pos / cell_count
        
        mal_severity = "severe" if mal_rate > 0.05 else "moderate" if mal_rate > 0.01 else "low"
        
        t_total = time.time() - t_total
        
        INFO("="*60)
        INFO("ANALYSIS COMPLETE!")
        INFO(f"Total: {t_total:.2f}s | Cells: {cell_count}")
        INFO(f"Malaria: {'+' if mal_pos > 0 else '-'} ({mal_pos}, {mal_rate*100:.1f}%)")
        INFO(f"Sickle: {'+' if sick_pos > 0 else '-'} ({sick_pos}, {sick_rate*100:.1f}%)")
        INFO(f"Elliptocytosis: {'+' if ellipt_pos > 0 else '-'} ({ellipt_pos}, {ellipt_rate*100:.1f}%)")
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
                'sickle_cell': {
                    'diagnosis': 'Positive' if sick_pos > 0 else 'Negative',
                    'confidence': round(float(sick_probs.mean()), 3),
                    'positive_rate': round(sick_rate, 3),
                    'positive_count': sick_pos,
                    'cell_distribution': {'normal': cell_count-sick_pos, 'sickle': sick_pos, 'target': 0, 'other': 0}
                },
                'elliptocytosis': {  # CHANGED FROM THALASSEMIA
                    'diagnosis': 'Positive' if ellipt_pos > 0 else 'Negative',
                    'confidence': round(float(ellipt_probs.mean()), 3),
                    'positive_rate': round(ellipt_rate, 3),
                    'positive_count': ellipt_pos,
                    'cell_distribution': {
                        'normal': cell_count - ellipt_pos,
                        'elliptocyte': int((ellipt_preds == 1).sum()),
                        'oval': int((ellipt_preds == 2).sum()),
                        'pencil_cigar': int((ellipt_preds == 3).sum())
                    }
                }
            },
            'quality_flags': [],
            'disclaimer': 'AI-assisted only. Not for clinical diagnosis.',
            'model_versions': {'segmentor': 'yolov8n', 'classifier': 'multi-disease-v2'}
        }


# Singleton
pipeline = None

def get_pipeline() -> OptimizedPipeline:
    global pipeline
    if pipeline is None:
        pipeline = OptimizedPipeline()
    return pipeline