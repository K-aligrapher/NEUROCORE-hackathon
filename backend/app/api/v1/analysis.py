import io
import logging
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from app.schemas.analysis import (
    AnalysisResult,
    AnalysisUploadResponse,
    CellStatistics,
    DiseasePrediction,
    HistoryItem,
    JobStatus as SchemaJobStatus,
)

logger = logging.getLogger("lokivision")
router = APIRouter(prefix="/analysis", tags=["Analysis"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB

# In-memory job store — keyed by job_id
# Each entry: {"status", "created_at", "completed_at"?, "processing_time_ms"?, "results"?, "error_message"?}
_jobs: Dict[str, Dict[str, Any]] = {}
_job_order: List[str] = []  # insertion order for history


def _new_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:8]}"


async def _process_image(job_id: str, image_bytes: bytes) -> None:
    try:
        _jobs[job_id]["status"] = "preprocessing"

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_array = np.array(image)

        _jobs[job_id]["status"] = "classifying"

        from app.ml.pipeline import get_pipeline
        result = get_pipeline().run(image_array)

        if result.get("status") == "completed":
            _jobs[job_id].update(
                status="completed",
                completed_at=datetime.utcnow().isoformat(),
                processing_time_ms=int(result["timing"]["total_s"] * 1000),
                results=result,
            )
        else:
            _jobs[job_id].update(status="failed", error_message=result.get("error", "Unknown error"))

    except Exception as exc:
        logger.error("Job %s failed: %s\n%s", job_id, exc, traceback.format_exc())
        _jobs[job_id].update(status="failed", error_message=str(exc))


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=AnalysisUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    if not image.filename:
        raise HTTPException(status_code=422, detail="No file provided")

    ext = Path(image.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    contents = await image.read()
    if len(contents) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    job_id = _new_job_id()
    _jobs[job_id] = {
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "patient_id": patient_id,
    }
    _job_order.append(job_id)

    background_tasks.add_task(_process_image, job_id, contents)

    return AnalysisUploadResponse(
        job_id=job_id,
        status=SchemaJobStatus.QUEUED,
        estimated_duration_seconds=30,
        websocket_url=f"ws://localhost:8000/ws/jobs/{job_id}",
        check_url=f"/api/v1/analysis/{job_id}",
    )


@router.get("/history", response_model=List[HistoryItem])
async def get_history(limit: int = 20):
    recent = list(reversed(_job_order))[:limit]
    items = []
    for jid in recent:
        job = _jobs.get(jid, {})
        items.append(
            HistoryItem(
                job_id=jid,
                status=SchemaJobStatus(job.get("status", "queued")),
                created_at=datetime.fromisoformat(job["created_at"]),
                completed_at=(
                    datetime.fromisoformat(job["completed_at"])
                    if job.get("completed_at")
                    else None
                ),
                patient_id=job.get("patient_id"),
                disease_results=["Malaria", "Thalassemia"] if job.get("status") == "completed" else [],
                processing_time_ms=job.get("processing_time_ms"),
            )
        )
    return items


@router.get("/{job_id}", response_model=AnalysisResult)
async def get_analysis(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    created_at = datetime.fromisoformat(job["created_at"])
    completed_at = (
        datetime.fromisoformat(job["completed_at"]) if job.get("completed_at") else None
    )

    _status_map = {
        "queued": SchemaJobStatus.QUEUED,
        "preprocessing": SchemaJobStatus.PREPROCESSING,
        "classifying": SchemaJobStatus.CLASSIFYING,
        "completed": SchemaJobStatus.COMPLETED,
        "failed": SchemaJobStatus.FAILED,
    }
    job_status = _status_map.get(job["status"], SchemaJobStatus.QUEUED)

    if job["status"] == "completed" and job.get("results"):
        ml = job["results"]
        cell_stats = CellStatistics(**ml["cell_statistics"])
        disease_results = {
            k: DiseasePrediction(**v) for k, v in ml["results"].items()
        }
        return AnalysisResult(
            job_id=job_id,
            status=job_status,
            created_at=created_at,
            completed_at=completed_at,
            processing_time_ms=job.get("processing_time_ms"),
            cell_statistics=cell_stats,
            results=disease_results,
            quality_flags=ml.get("quality_flags", []),
            overall_recommendation=ml.get("disclaimer"),
            disclaimer=ml.get("disclaimer"),
        )

    return AnalysisResult(
        job_id=job_id,
        status=job_status,
        created_at=created_at,
        completed_at=completed_at,
        processing_time_ms=job.get("processing_time_ms"),
        error_message=job.get("error_message"),
        quality_flags=[],
        disclaimer="AI-assisted screening. Not for clinical diagnosis.",
    )
