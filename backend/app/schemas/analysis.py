from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    CLASSIFYING = "classifying"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisUploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    estimated_duration_seconds: int = 30
    websocket_url: str
    check_url: str


class CellStatistics(BaseModel):
    total_detected: int = 0
    rbc_count: int = 0
    wbc_count: int = 0
    platelet_count: int = 0
    rejected_count: int = 0


class DiseasePrediction(BaseModel):
    diagnosis: str
    confidence: float
    positive_rate: Optional[float] = None
    positive_count: Optional[int] = None
    cell_distribution: Optional[Dict[str, int]] = None
    severity: Optional[str] = None


class AnalysisResult(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    cell_statistics: Optional[CellStatistics] = None
    results: Optional[Dict[str, DiseasePrediction]] = None
    quality_flags: List[str] = []
    overall_recommendation: Optional[str] = None
    disclaimer: Optional[str] = None


class HistoryItem(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    patient_id: Optional[str] = None
    disease_results: List[str] = []
    processing_time_ms: Optional[int] = None
