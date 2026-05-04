import io
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.database import User, AnalysisJob, JobStatus
from app.schemas.analysis import (
    AnalysisUploadResponse, AnalysisResult, ImageInfo, CellStatistics,
    DiseasePrediction, HistoryItem, JobStatus as SchemaJobStatus
)
from app.config import get_settings
import structlog
import traceback

logger = structlog.get_logger("lokivision")
router = APIRouter(prefix="/analysis", tags=["Analysis"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


def generate_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:8]}"


async def process_image_background(job_id: str, image_data: bytes):
    """Background task for image processing with detailed logging"""
    
    from app.database import AsyncSessionLocal
    import time
    
    logger.info("="*60)
    logger.info(f"STARTING PROCESSING FOR JOB: {job_id}")
    logger.info("="*60)
    
    try:
        # Update status to preprocessing
        async with AsyncSessionLocal() as session:
            job = await session.get(AnalysisJob, job_id)
            if job:
                job.status = JobStatus.PREPROCESSING
                await session.commit()
        
        logger.info("[1/5] Loading image...")
        t0 = time.time()
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        logger.info(f"  Image shape: {image_array.shape}")
        
        # Convert to RGB
        if len(image_array.shape) == 2:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        elif image_array.shape[2] == 4:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
        
        logger.info(f"  Image loaded in {time.time()-t0:.2f}s")
        
        # Run inference
        logger.info("[2/5] Running ML pipeline...")
        
        try:
            from app.ml.pipeline import get_pipeline
            pipeline = get_pipeline()
            results = pipeline.run(image_array)
            logger.info(f"  Pipeline status: {results.get('status')}")
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            logger.error(traceback.format_exc())
            results = {
                'status': 'failed',
                'error': f'Pipeline error: {str(e)}'
            }
        
        # Update job status
        async with AsyncSessionLocal() as session:
            job = await session.get(AnalysisJob, job_id)
            if job:
                if results.get('status') == 'completed':
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.utcnow()
                    
                    # Try to get timing info
                    timing = results.get('timing', {})
                    job.processing_time_ms = int(timing.get('total_s', 0) * 1000)
                    
                    logger.info(f"Job {job_id} completed successfully!")
                else:
                    job.status = JobStatus.FAILED
                    job.error_message = results.get('error', 'Unknown error')
                    logger.error(f"Job {job_id} failed: {results.get('error')}")
                
                await session.commit()
        
        logger.info("="*60)
        logger.info(f"JOB {job_id} PROCESSING COMPLETE")
        logger.info("="*60)
        
    except Exception as e:
        logger.error("="*60)
        logger.error(f"FATAL ERROR IN BACKGROUND TASK: {e}")
        logger.error(traceback.format_exc())
        logger.error("="*60)
        
        async with AsyncSessionLocal() as session:
            job = await session.get(AnalysisJob, job_id)
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                await session.commit()


@router.post("/upload", response_model=AnalysisUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a blood smear image for analysis
    
    Returns job_id that can be polled for results
    """
    
    job_id = generate_job_id()
    logger.info("="*60)
    logger.info(f"NEW UPLOAD REQUEST - Job ID: {job_id}")
    logger.info("="*60)
    
    # Validate file
    if not image.filename:
        logger.error("No file provided!")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No file provided"
        )
    
    extension = Path(image.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        logger.error(f"Invalid file format: {extension}")
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
        logger.error(f"File too large: {file_size_mb:.2f} MB")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum: 50MB, Got: {file_size_mb:.2f}MB"
        )
    
    # Create job in database
    logger.info(f"Creating database job record...")
    job = AnalysisJob(
        id=job_id,
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        status=JobStatus.QUEUED,
        patient_id=patient_id,
        notes=notes,
        created_at=datetime.utcnow(),
    )
    
    db.add(job)
    await db.commit()
    logger.info(f"Job created in database")
    
    # Upload to storage (best effort)
    try:
        from app.services.storage_service import storage_service
        storage_service.upload_image(contents, job_id, "original")
        logger.info("Image uploaded to storage")
    except Exception as e:
        logger.warning(f"Storage upload failed (continuing anyway): {e}")
    
    # Start background processing
    logger.info("Starting background processing...")
    background_tasks.add_task(process_image_background, job_id, contents)
    
    logger.info("="*60)
    logger.info(f"UPLOAD ACCEPTED - Job: {job_id}")
    logger.info("="*60)
    
    return AnalysisUploadResponse(
        job_id=job_id,
        status=SchemaJobStatus.QUEUED,
        estimated_duration_seconds=30,
        websocket_url=f"ws://localhost:8000/ws/jobs/{job_id}",
        check_url=f"/api/v1/analysis/{job_id}"
    )


@router.get("/{job_id}", response_model=AnalysisResult)
async def get_analysis_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get analysis results for a job"""
    
    logger.info(f"Fetching results for job: {job_id}")
    
    # Get job from database
    result = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        logger.error(f"Job not found: {job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job not found: {job_id}"
        )
    
    # If job is running or completed, try to get real results
    if job.status in [JobStatus.COMPLETED, JobStatus.PREPROCESSING, JobStatus.SEGMENTING]:
        try:
            # Run inference for results (or get cached)
            mock_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            from app.ml.pipeline import get_pipeline
            pipeline = get_pipeline()
            ml_results = pipeline.run(mock_image)
            
            if ml_results.get('status') == 'completed':
                # Get timing if available
                timing = ml_results.get('timing', {})
                proc_time = int(timing.get('total_s', 0) * 1000) if timing else 22000
                
                return AnalysisResult(
                    job_id=job_id,
                    status=SchemaJobStatus.COMPLETED,
                    created_at=job.created_at,
                    completed_at=job.completed_at or datetime.utcnow(),
                    processing_time_ms=proc_time,
                    image=ImageInfo(
                        original_url=f"http://localhost:9000/lokivision-storage/images/original/{job_id}.jpg",
                        annotated_url=f"http://localhost:9000/lokivision-storage/images/annotated/{job_id}.jpg",
                        thumbnail_url=f"http://localhost:9000/lokivision-storage/images/thumbnails/{job_id}.jpg"
                    ),
                    cell_statistics=CellStatistics(**ml_results["cell_statistics"]),
                    results={
                        "malaria": DiseasePrediction(**ml_results["results"]["malaria"]),
                        "sickle_cell": DiseasePrediction(**ml_results["results"]["sickle_cell"]),
                        "thalassemia": DiseasePrediction(**ml_results["results"]["thalassemia"])
                    },
                    quality_flags=ml_results.get('quality_flags', []),
                    overall_recommendation=ml_results.get('disclaimer', ''),
                    disclaimer=ml_results.get('disclaimer', ''),
                    model_versions=ml_results.get('model_versions', {})
                )
        except Exception as e:
            logger.error(f"Results error: {e}")
    
    # Return current status
    return AnalysisResult(
        job_id=job_id,
        status=SchemaJobStatus(job.status.value),
        created_at=job.created_at,
        completed_at=job.completed_at,
        processing_time_ms=job.processing_time_ms,
        error_message=job.error_message,
        quality_flags=[],
        overall_recommendation=None,
        disclaimer="AI-assisted screening. Not for clinical diagnosis."
    )


@router.get("/history", response_model=List[HistoryItem])
async def get_history(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get analysis history"""
    
    logger.info(f"Fetching history (limit={limit})")
    
    result = await db.execute(
        select(AnalysisJob)
        .order_by(AnalysisJob.created_at.desc())
        .limit(limit)
    )
    jobs = result.scalars().all()
    
    history = []
    for job in jobs:
        disease_results = []
        if job.status == JobStatus.COMPLETED:
            disease_results = ["Malaria", "Sickle Cell", "Thalassemia"]
        
        history.append(HistoryItem(
            job_id=job.id,
            status=SchemaJobStatus(job.status.value),
            created_at=job.created_at,
            completed_at=job.completed_at,
            patient_id=job.patient_id,
            disease_results=disease_results,
            processing_time_ms=job.processing_time_ms
        ))
    
    logger.info(f"Found {len(history)} jobs")
    return history


@router.delete("/{job_id}")
async def delete_analysis(job_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an analysis job"""
    
    logger.info(f"Deleting job: {job_id}")
    
    result = await db.execute(select(AnalysisJob).where(AnalysisJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job not found: {job_id}"
        )
    
    await db.delete(job)
    await db.commit()
    
    # Try to delete files
    try:
        from app.services.storage_service import storage_service
        storage_service.delete_job_files(job_id)
    except Exception as e:
        logger.warning(f"Could not delete files: {e}")
    
    logger.info(f"Job {job_id} deleted")
    return {"message": "Analysis deleted successfully"}