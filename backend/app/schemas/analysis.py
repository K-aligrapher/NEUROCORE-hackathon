from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    SEGMENTING = "segmenting"
    ENHANCING = "enhancing"
    CLASSIFYING = "classifying"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str
    role: UserRole = UserRole.CLINICIAN
    institution: Optional[str] = None
    country: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    institution: Optional[str] = None
    country: Optional[str] = None
    is_verified: bool = False
    created_at: datetime


class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    iat: int
    exp: int
    jti: str


# Analysis Schemas
class AnalysisUpload(BaseModel):
    patient_id: Optional[str] = None
    notes: Optional[str] = None


class AnalysisUploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    estimated_duration_seconds: int = 25
    websocket_url: str
    check_url: str


class ImageInfo(BaseModel):
    original_url: Optional[str] = None
    annotated_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


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
    severity_description: Optional[str] = None
    species_hint: Optional[str] = None


class AnalysisResult(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    device: Optional[str] = None
    timing: Optional[Dict[str, float]] = None
    image: Optional[ImageInfo] = None
    cell_statistics: Optional[CellStatistics] = None
    results: Optional[Dict[str, DiseasePrediction]] = None
    quality_flags: List[str] = []
    overall_recommendation: Optional[str] = None
    disclaimer: Optional[str] = None
    model_versions: Optional[Dict[str, str]] = None


class DiseaseResultResponse(BaseModel):
    disease: str
    diagnosis: str
    confidence: float
    positive_rate: float
    positive_count: int
    total_analyzed: int
    severity: Optional[str] = None
    raw_distribution: Dict[str, int] = {}
    model_version: str


class CellDetectionResponse(BaseModel):
    id: str
    cell_index: int
    cell_type: str
    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int
    area_px: Optional[int] = None
    circularity: Optional[float] = None
    cell_crop_url: Optional[str] = None
    malaria_prediction: Optional[str] = None
    malaria_confidence: Optional[float] = None
    sickle_prediction: Optional[str] = None
    sickle_confidence: Optional[float] = None
    thal_prediction: Optional[str] = None
    thal_confidence: Optional[float] = None


class HistoryItem(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    patient_id: Optional[str] = None
    disease_results: List[str] = []
    processing_time_ms: Optional[int] = None


class BatchUploadResponse(BaseModel):
    batch_id: str
    job_ids: List[str]
    total_images: int
    status: str


# Error Schemas
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# WebSocket Schemas
class WSProgressMessage(BaseModel):
    type: str = "progress"
    stage: str
    progress: float
    message: str


class WSStageComplete(BaseModel):
    type: str = "stage_complete"
    stage: str
    cell_count: int
    duration_ms: int


class WSError(BaseModel):
    type: str = "error"
    code: str
    message: str


class WSComplete(BaseModel):
    type: str = "complete"
    job_id: str
    result_url: str