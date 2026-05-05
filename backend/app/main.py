import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.analysis import router as analysis_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("lokivision")

settings = get_settings()

app = FastAPI(
    title="LokiVision API",
    description="Blood Smear Analysis — Malaria & Thalassemia Detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": "LokiVision API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    return {"name": "LokiVision", "docs": "/docs"}
