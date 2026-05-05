import time
import logging
from pathlib import Path
from typing import List, Dict, Optional

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torchvision.models import efficientnet_b0

logger = logging.getLogger("lokivision")

IMG_SIZE = 128
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"

# Malaria: 0=Negative (uninfected), 1=Positive (parasitized)
MALARIA_CLASSES = {0: "negative", 1: "positive"}
# Thalassemia: 0=Abnormal, 1=Normal
THAL_CLASSES = {0: "abnormal", 1: "normal"}

INFERENCE_TRANSFORM = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _build_efficientnet(num_classes: int) -> nn.Module:
    """Recreate the exact architecture used during training."""
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features  # 1280
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 256),
        nn.ReLU(),
        nn.BatchNorm1d(256),
        nn.Dropout(0.2),
        nn.Linear(256, num_classes),
    )
    return model


def _load_checkpoint(path: Path, num_classes: int, device: str) -> nn.Module:
    model = _build_efficientnet(num_classes)
    if path.exists():
        try:
            ckpt = torch.load(path, map_location=device)
            state = ckpt.get("model_state_dict", ckpt)
            model.load_state_dict(state)
            logger.info("Loaded %s", path.name)
        except Exception as exc:
            logger.error("Could not load %s: %s — using random weights", path.name, exc)
    else:
        logger.warning("Model not found at %s — using random weights", path)
    model.eval()
    return model.to(device)


def _detect_cells(image: np.ndarray) -> List[np.ndarray]:
    """Extract individual cell crops from a blood smear using OpenCV."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    crops: List[np.ndarray] = []
    for cnt in contours:
        if not (200 < cv2.contourArea(cnt) < 8000):
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        pad = 5
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(image.shape[1], x + w + pad)
        y2 = min(image.shape[0], y + h + pad)
        crop = image[y1:y2, x1:x2]
        if crop.size > 0:
            crops.append(crop)
        if len(crops) >= 200:
            break

    return crops


def _classify_batch(crops: List[np.ndarray], model: nn.Module, device: str) -> np.ndarray:
    """Return softmax probability matrix (N, num_classes)."""
    tensors = [INFERENCE_TRANSFORM(c) for c in crops]
    batch = torch.stack(tensors).to(device)
    with torch.no_grad():
        probs = F.softmax(model(batch), dim=1)
    return probs.cpu().numpy()


class BloodSmearPipeline:
    def __init__(self) -> None:
        self.device = self._pick_device()
        logger.info("Pipeline device: %s", self.device)
        logger.info("Loading models from %s", MODEL_DIR)
        self.malaria_model = _load_checkpoint(
            MODEL_DIR / "malaria_model.pt", num_classes=2, device=self.device
        )
        self.thal_model = _load_checkpoint(
            MODEL_DIR / "thalassemia_model.pt", num_classes=2, device=self.device
        )

    @staticmethod
    def _pick_device() -> str:
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def run(self, image: np.ndarray) -> Dict:
        t0 = time.time()

        # Normalise colour channels
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        # Cell detection
        crops = _detect_cells(image)
        if not crops:
            # Fall back: treat whole image as one "cell"
            logger.warning("No cells detected — falling back to whole-image classification")
            crops = [image]

        n = len(crops)
        logger.info("Analysing %d cells", n)

        # Malaria inference  (class 1 = parasitized / positive)
        mal_probs = _classify_batch(crops, self.malaria_model, self.device)
        mal_pos_count = int((mal_probs.argmax(axis=1) == 1).sum())
        mal_rate = mal_pos_count / n
        mal_conf = float(mal_probs[:, 1].mean())

        # Thalassemia inference  (class 0 = abnormal / positive)
        thal_probs = _classify_batch(crops, self.thal_model, self.device)
        thal_pos_count = int((thal_probs.argmax(axis=1) == 0).sum())
        thal_rate = thal_pos_count / n
        thal_conf = float(thal_probs[:, 0].mean())

        # Thresholds
        mal_diagnosis = "Positive" if mal_rate > 0.01 else "Negative"
        mal_severity = (
            "severe" if mal_rate > 0.05 else "moderate" if mal_rate > 0.01 else "low"
        )
        thal_diagnosis = "Positive" if thal_rate > 0.10 else "Negative"

        elapsed = round(time.time() - t0, 2)
        logger.info(
            "Done in %.2fs — Malaria: %s (%.1f%%)  Thalassemia: %s (%.1f%%)",
            elapsed, mal_diagnosis, mal_rate * 100, thal_diagnosis, thal_rate * 100,
        )

        return {
            "status": "completed",
            "device": self.device,
            "timing": {"total_s": elapsed},
            "cell_statistics": {
                "total_detected": n,
                "rbc_count": n,
                "wbc_count": 0,
                "platelet_count": 0,
                "rejected_count": 0,
            },
            "results": {
                "malaria": {
                    "diagnosis": mal_diagnosis,
                    "confidence": round(mal_conf, 3),
                    "positive_rate": round(mal_rate, 3),
                    "positive_count": mal_pos_count,
                    "severity": mal_severity,
                    "cell_distribution": {
                        "parasitized": mal_pos_count,
                        "uninfected": n - mal_pos_count,
                    },
                },
                "thalassemia": {
                    "diagnosis": thal_diagnosis,
                    "confidence": round(thal_conf, 3),
                    "positive_rate": round(thal_rate, 3),
                    "positive_count": thal_pos_count,
                    "cell_distribution": {
                        "normal": n - thal_pos_count,
                        "abnormal": thal_pos_count,
                    },
                },
            },
            "quality_flags": [],
            "disclaimer": (
                "AI-assisted screening only. Results must be reviewed by a qualified clinician."
            ),
        }


_pipeline: Optional[BloodSmearPipeline] = None


def get_pipeline() -> BloodSmearPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = BloodSmearPipeline()
    return _pipeline
