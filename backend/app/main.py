from datetime import datetime
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import init_db
import structlog

from app.api.v1.auth import router as auth_router
from app.api.v1.analysis import router as analysis_router

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LokiVision API")
    
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning("Database init skipped", error=str(e))
    
    yield
    
    logger.info("Shutting down LokiVision API")


app = FastAPI(
    title="LokiVision API",
    description="Blood Smear Analysis & Disease Detection System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LokiVision API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    return {
        "name": "LokiVision",
        "description": "Blood Smear Analysis & Disease Detection System",
        "version": "1.0.0",
        "docs": "/docs"
    }


app.include_router(auth_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": str(uuid.uuid4())
            }
        }
    )