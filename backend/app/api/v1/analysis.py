import io
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
import time

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from app.config import get_settings
import structlog
import traceback

logger = structlog.get_logger("lokivision")
router = APIRouter(prefix="/analysis", tags=["Analysis"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


@router.post("/upload")
async def upload_and_analyze(
    image: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """
    Upload a blood smear image and get analysis results directly.
    No database, no background tasks — just image in, results out.
    """

    job_id = f"job_{uuid.uuid4().hex[:8]}"

    logger.info("=" * 60)
    logger.info(f"NEW ANALYSIS REQUEST - Job ID: {job_id}")
    logger.info("=" * 60)

    # Validate file
    if not image.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No file provided"
        )

    extension = Path(image.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file format. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file
    logger.info(f"Reading file: {image.filename}")
    contents = await image.read()
    file_size_mb = len(contents) / (1024 * 1024)
    logger.info(f"File size: {file_size_mb:.2f} MB")

    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum: 50MB, Got: {file_size_mb:.2f}MB"
        )

    # Load and convert image
    try:
        pil_image = Image.open(io.BytesIO(contents))
        image_array = np.array(pil_image)
        logger.info(f"Image shape: {image_array.shape}")

        # Convert to RGB
        if len(image_array.shape) == 2:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        elif image_array.shape[2] == 4:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
    except Exception as e:
        logger.error(f"Failed to load image: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not read image: {str(e)}"
        )

    # Run ML pipeline directly
    try:
        from app.ml.pipeline import get_pipeline
        pipeline = get_pipeline()
        results = pipeline.run(image_array)
        logger.info(f"Pipeline status: {results.get('status')}")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

    if results.get('status') != 'completed':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=results.get('error', 'Analysis could not complete')
        )

    # Return results directly
    return {
        "job_id": job_id,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "device": results.get("device"),
        "timing": results.get("timing"),
        "cell_statistics": results.get("cell_statistics"),
        "results": results.get("results"),
        "quality_flags": results.get("quality_flags", []),
        "disclaimer": results.get("disclaimer", "AI-assisted only. Not for clinical diagnosis."),
        "model_versions": results.get("model_versions"),
    }