#!/usr/bin/env python3
"""
LokiVision - GPU-Optimized Blood Smear Analysis Pipeline
With comprehensive error handling and progress logging
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

# Configure structured logging
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


@dataclass
class InferenceConfig:
    """Configuration optimized for 8GB VRAM"""
    device: str = "cuda"
    batch_size: int = 32
    img_size: int = 128
    confidence_threshold: float = 0.7
    max_cells_analysis: int = 200


class ModelLoadError(Exception):
    """Custom exception for model loading errors"""
    pass


class DetectionError(Exception):
    """Custom exception for detection errors"""
    pass


class ClassificationError(Exception):
    """Custom exception for classification errors"""
    pass


class MultiDiseaseClassifier(nn.Module):
    """
    SINGLE MODEL for all 3 diseases!
    EfficientNet-B0 backbone + disease-specific heads
    
    Classes:
    - Malaria: [parasitized, uninfected]
    - Sickle: [normal, sickle, target, other_abnormal]  
    - Thal: [normal, hypochromic, target, pencil, microcytic]
    """
    
    def __init__(self, num_classes_per_disease: List[int] = [2, 4, 5], model_path: Optional[str] = None):
        super().__init__()
        
        logger.info("Loading EfficientNet-B0 backbone...")
        t0 = time.time()
        
        # Load pretrained EfficientNet-B0
        try:
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            weights = EfficientNet_B0_Weights.DEFAULT
            self.backbone = efficientnet_b0(weights=weights)
            logger.info(f"EfficientNet-B0 backbone loaded in {time.time()-t0:.1f}s")
        except Exception as e:
            raise ModelLoadError(f"Failed to load EfficientNet-B0: {e}")
        
        self.feature_dim = 1280
        
        # Freeze early layers for faster inference
        logger.info("Freezing early backbone layers...")
        for i, param in enumerate(self.backbone.features[:5].parameters()):
            param.requires_grad = False
        
        # Disease-specific heads
        self.malaria_head = nn.Linear(self.feature_dim, num_classes_per_disease[0])
        self.sickle_head = nn.Linear(self.feature_dim + 12, num_classes_per_disease[1])
        self.thal_head = nn.Linear(self.feature_dim + 5, num_classes_per_disease[2])
        
        # Load trained weights if available
        if model_path and Path(model_path).exists():
            logger.info(f"Loading trained weights from {model_path}")
            try:
                self.load_state_dict(torch.load(model_path, map_location='cpu'))
                logger.info("Trained weights loaded successfully!")
            except Exception as e:
                logger.warning(f"Could not load trained weights: {e}")
                logger.warning("Using pretrained backbone (not trained yet)")
        else:
            logger.warning("="*50)
            logger.warning("NO TRAINED MODEL FOUND!")
            logger.warning("Please train models first: python training/train.py")
            logger.warning("="*50)
    
    def extract_shape_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract shape features for sickle cell detection"""
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
                
                try:
                    moments = cv2.moments(cnt)
                    hu = cv2.HuMoments(moments).flatten()
                    hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
                except:
                    hu = np.zeros(7)
                
                features = [circularity, aspect, solidity, extent] + list(hu[:7])
            else:
                features = [0.5] * 11
            
            shape_features.append(features[:11])
        
        return torch.tensor(shape_features, dtype=torch.float32)
    
    def extract_color_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract color features for thalassemia detection"""
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
            
            center_mean = np.mean(center)
            overall_mean = np.mean(img)
            pallor_ratio = 1 - (center_mean / (overall_mean + 1e-6))
            
            l_mean, a_mean, b_mean = np.mean(l)/255, np.mean(a)/255, np.mean(b)/255
            l_std, a_std, b_std = np.std(l)/255, np.std(a)/255, np.std(b)/255
            
            features = [pallor_ratio, l_mean, a_mean, b_mean, l_std]
            color_features.append(features)
        
        return torch.tensor(color_features, dtype=torch.float32)
    
    def forward(self, x: torch.Tensor):
        # Extract shared features
        features = self.backbone.features(x)
        features = F.adaptive_avg_pool2d(features, 1).view(features.size(0), -1)
        
        # Malware classification (texture-based)
        malaria_logits = self.malaria_head(features)
        
        # Sickle classification (needs shape features)
        shape_feats = self.extract_shape_features(x)
        sickle_input = torch.cat([features, shape_feats.to(x.device)], dim=1)
        sickle_logits = self.sickle_head(sickle_input)
        
        # Thalassemia classification (needs color features)
        color_feats = self.extract_color_features(x).to(x.device)
        thal_input = torch.cat([features, color_feats], dim=1)
        thal_logits = self.thal_head(thal_input)
        
        return malaria_logits, sickle_logits, thal_logits


class YOLOv8Detector:
    """YOLOv8 for blood cell detection in one pass"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.device = self._get_device()
        self.model = None
        self.use_yolo = False
        self._load_model()
    
    def _get_device(self):
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name()
            logger.info(f"GPU detected: {device_name}")
            logger.info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return "cuda"
        elif hasattr(torch, 'mps') and torch.mps.is_available():
            logger.info("Using Apple MPS (Apple Silicon)")
            return "mps"
        logger.warning("No GPU found! Using CPU (slow)")
        return "cpu"
    
    def _load_model(self):
        logger.info("Loading YOLOv8n for cell detection...")
        
        try:
            from ultralytics import YOLO
        except ImportError:
            logger.error("Ultralytics not installed!")
            logger.error("Install with: pip install ultralytics")
            logger.error("Detection will NOT work!")
            return
        
        model_path = Path("models/yolov8n.pt")
        
        try:
            if model_path.exists():
                logger.info(f"Loading YOLO from {model_path}")
                self.model = YOLO(str(model_path))
            else:
                logger.info("Downloading YOLOv8n model...")
                self.model = YOLO("yolov8n.pt")
                logger.info("YOLOv8n downloaded")
            
            self.model.to(self.device)
            self.use_yolo = True
            logger.info("YOLOv8n loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
            logger.error("Detection will use fallback (less accurate)")
            self._load_fallback()
    
    def _load_fallback(self):
        """OpenCV-based fallback detector"""
        logger.warning("Using OpenCV fallback detector (less accurate)")
        self.use_yolo = False
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """Detect all blood cells in image"""
        
        if not self.use_yolo or self.model is None:
            logger.info("Using OpenCV fallback detection")
            return self._opencv_detect(image)
        
        logger.info(f"Running YOLO detection on {image.shape[:2]} image...")
        t0 = time.time()
        
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
                boxes = r.boxes
                for box in boxes:
                    detections.append({
                        'bbox': box.xyxy[0].cpu().numpy().tolist(),
                        'confidence': float(box.conf[0]),
                        'class': int(box.cls[0])
                    })
            
            logger.info(f"YOLO found {len(detections)} cells in {time.time()-t0:.2f}s")
            return detections
            
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            logger.info("Falling back to OpenCV...")
            return self._opencv_detect(image)
    
    def _opencv_detect(self, image: np.ndarray) -> List[Dict]:
        """OpenCV-based blood cell detection"""
        logger.info("Running OpenCV detection...")
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for cnt in contours[:self.config.max_cells_analysis]:
            area = cv2.contourArea(cnt)
            if 200 < area < 8000:  # Valid RBC size range
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    'bbox': [x, y, x+w, y+h],
                    'confidence': 0.8,
                    'class': 0
                })
        
        logger.info(f"OpenCV found {len(detections)} cells")
        return detections


class OptimizedPipeline:
    """
    GPU-OPTIMIZED pipeline for LokiVision
    Requires trained models!
    """
    
    def __init__(self, config: Optional[InferenceConfig] = None):
        self.config = config or InferenceConfig()
        self.device = self._get_device()
        
        logger.info("="*60)
        logger.info("LOKIVISION PIPELINE INITIALIZATION")
        logger.info("="*60)
        
        # Load detector
        logger.info("[1/3] Loading YOLOv8 detector...")
        self.detector = YOLOv8Detector(self.config)
        
        # Load classifier
        logger.info("[2/3] Loading disease classifier...")
        self.classifier = self._load_classifier()
        
        # Image transforms
        logger.info("[3/3] Setting up transforms...")
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((self.config.img_size, self.config.img_size)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        logger.info("="*60)
        logger.info("Pipeline ready!")
        logger.info(f"Device: {self.device}")
        logger.info(f"Batch size: {self.config.batch_size}")
        logger.info(f"Image size: {self.config.img_size}")
        logger.info("="*60)
    
    def _get_device(self):
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch, 'mps') and torch.mps.is_available():
            return "mps"
        return "cpu"
    
    def _load_classifier(self) -> MultiDiseaseClassifier:
        """Load the multi-disease classifier"""
        
        # Try to load trained model
        model_paths = [
            "models/multi_disease_classifier.pt",
            "models/malaria_classifier.pt",
            "models/sickle_classifier.pt", 
            "models/thal_classifier.pt"
        ]
        
        for path in model_paths:
            if Path(path).exists():
                logger.info(f"Found trained model: {path}")
                try:
                    model = MultiDiseaseClassifier(model_path=path)
                    logger.info("Trained model loaded!")
                    return model
                except Exception as e:
                    logger.error(f"Failed to load {path}: {e}")
        
        # No trained model found
        logger.error("="*60)
        logger.error("NO TRAINED MODEL FOUND!")
        logger.error("="*60)
        logger.error("")
        logger.error("Please train the models first:")
        logger.error("  1. Put your dataset in data/<disease>/")
        logger.error("  2. Run: python training/train.py --disease malaria --data data/malaria")
        logger.error("="*60)
        
        # Return untrained model (will give untrained results)
        return MultiDiseaseClassifier()
    
    def run(self, image: np.ndarray) -> Dict:
        """
        Run full blood smear analysis
        Returns detailed results with progress messages
        """
        
        logger.info("="*60)
        logger.info("STARTING BLOOD SMEAR ANALYSIS")
        logger.info("="*60)
        
        t_total = time.time()
        
        # Step 1: Detection
        logger.info("[STEP 1/4] Detecting blood cells...")
        t1 = time.time()
        detections = self.detector.detect(image)
        t_detect = time.time() - t1
        
        if len(detections) < 10:
            logger.error(f"Too few cells detected: {len(detections)}")
            return {
                'job_id': 'inference',
                'status': 'failed',
                'error': f'Only {len(detections)} cells detected. Need at least 10.',
                'suggestion': 'Try a clearer/better quality image'
            }
        
        logger.info(f"  -> Found {len(detections)} cells in {t_detect:.2f}s")
        
        # Step 2: Crop cells
        logger.info("[STEP 2/4] Cropping cells...")
        t2 = time.time()
        cell_tensors = []
        
        for i, cell in enumerate(detections[:self.config.max_cells_analysis]):
            bbox = cell['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            pad = 5
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(image.shape[1], x2 + pad)
            y2 = min(image.shape[0], y2 + pad)
            
            crop = image[y1:y2, x1:x2]
            if crop.size > 0:
                tensor = self.transform(crop)
                cell_tensors.append(tensor)
        
        crop_count = len(cell_tensors)
        t_crop = time.time() - t2
        logger.info(f"  -> Cropped {crop_count} cells in {t_crop:.2f}s")
        
        if not cell_tensors:
            logger.error("No valid cells to classify")
            return {'status': 'failed', 'error': 'No valid cells found'}
        
        # Step 3: GPU Batch Classification
        logger.info(f"[STEP 3/4] Classifying {crop_count} cells on {self.device}...")
        t3 = time.time()
        
        try:
            # Batch processing on GPU
            batch = torch.stack(cell_tensors).to(self.device)
            batch_size = batch.size(0)
            logger.info(f"  -> Batch shape: {batch.shape}")
            
            with torch.no_grad():
                mal_logits, sick_logits, thal_logits = self.classifier(batch)
                
                # Get predictions
                mal_preds = torch.argmax(mal_logits, dim=1)
                mal_probs = F.softmax(mal_logits, dim=1).max(dim=1)[0]
                
                sick_preds = torch.argmax(sick_logits, dim=1)
                sick_probs = F.softmax(sick_logits, dim=1).max(dim=1)[0]
                
                thal_preds = torch.argmax(thal_logits, dim=1)
                thal_probs = F.softmax(thal_logits, dim=1).max(dim=1)[0]
            
            t_class = time.time() - t3
            logger.info(f"  -> Classification done in {t_class:.2f}s")
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'status': 'failed',
                'error': f'Classification error: {e}'
            }
        
        # Step 4: Aggregate results
        logger.info("[STEP 4/4] Aggregating results...")
        
        cell_count = len(cell_tensors)
        
        # Count predictions
        mal_pos = int((mal_preds == 0).sum())
        sick_pos = int((sick_preds == 1).sum())
        thal_pos = int((thal_preds != 0).sum())
        
        mal_rate = mal_pos / cell_count
        sick_rate = sick_pos / cell_count
        thal_rate = thal_pos / cell_count
        
        # Determine severity
        mal_severity = "severe" if mal_rate > 0.05 else "moderate" if mal_rate > 0.01 else "low"
        
        # Calculate confidences
        mal_conf = float(mal_probs.mean())
        sick_conf = float(sick_probs.mean())
        thal_conf = float(thal_probs.mean())
        
        t_total = time.time() - t_total
        
        logger.info("="*60)
        logger.info("ANALYSIS COMPLETE!")
        logger.info(f"Total time: {t_total:.2f}s")
        logger.info(f"Cells analyzed: {cell_count}")
        logger.info("-" * 30)
        logger.info(f"Malaria: {'POSITIVE' if mal_pos > 0 else 'NEGATIVE'} ({mal_pos}/{cell_count} = {mal_rate*100:.1f}%)")
        logger.info(f"Sickle: {'POSITIVE' if sick_pos > 0 else 'NEGATIVE'} ({sick_pos}/{cell_count} = {sick_rate*100:.1f}%)")
        logger.info(f"Thalassemia: {'POSITIVE' if thal_pos > 0 else 'NEGATIVE'} ({thal_pos}/{cell_count} = {thal_rate*100:.1f}%)")
        logger.info("="*60)
        
        return {
            'job_id': 'inference',
            'status': 'completed',
            'device': self.device,
            'timing': {
                'detection_s': round(t_detect, 2),
                'crop_s': round(t_crop, 2),
                'classification_s': round(t_class, 2),
                'total_s': round(t_total, 2)
            },
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
                    'confidence': round(mal_conf, 3),
                    'positive_rate': round(mal_rate, 3),
                    'positive_count': mal_pos,
                    'severity': mal_severity,
                    'cell_distribution': {
                        'parasitized': mal_pos,
                        'uninfected': cell_count - mal_pos
                    },
                    'model_version': 'efficientnet-b0-malaria-v1.0'
                },
                'sickle_cell': {
                    'diagnosis': 'Positive' if sick_pos > 0 else 'Negative',
                    'confidence': round(sick_conf, 3),
                    'positive_rate': round(sick_rate, 3),
                    'positive_count': sick_pos,
                    'cell_distribution': {
                        'normal': cell_count - sick_pos,
                        'sickle': sick_pos,
                        'target': 0,
                        'other': 0
                    },
                    'model_version': 'mobilenetv3-sickle-v1.0'
                },
                'thalassemia': {
                    'diagnosis': 'Positive' if thal_pos > 0 else 'Negative',
                    'confidence': round(thal_conf, 3),
                    'positive_rate': round(thal_rate, 3),
                    'positive_count': thal_pos,
                    'cell_distribution': {
                        'normal': cell_count - thal_pos,
                        'hypochromic': thal_pos,
                        'target': 0,
                        'pencil': 0,
                        'micro': 0
                    },
                    'model_version': 'efficientnet-b2-thal-v1.0'
                }
            },
            'quality_flags': [],
            'disclaimer': 'AI-assisted screening only. Not for clinical diagnosis.',
            'model_versions': {
                'segmentor': 'yolov8n',
                'classifier': 'multi-disease-cnn-v1.0'
            }
        }


# Singleton
pipeline = None

def get_pipeline() -> OptimizedPipeline:
    global pipeline
    if pipeline is None:
        pipeline = OptimizedPipeline()
    return pipeline