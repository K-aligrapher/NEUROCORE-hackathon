from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "LokiVision"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"

    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "lokivision"
    POSTGRES_USER: str = "lokivision"
    POSTGRES_PASSWORD: str = "lokivision_dev_password_2024"
    DATABASE_URL: str = "postgresql+asyncpg://lokivision:lokivision_dev_password_2024@db:5432/lokivision"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "lokivision_redis_password_2024"
    REDIS_URL: str = "redis://:lokivision_redis_password_2024@redis:6379"

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "lokivision_minio_password_2024"
    MINIO_BUCKET: str = "lokivision-storage"
    MINIO_SECURE: bool = False

    JWT_SECRET: str = "lokivision-jwt-secret-min-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MODEL_DIR: str = "/app/models"
    SEGMENTOR_MODEL: str = "yolov8n-blood.pt"
    MALARIA_MODEL: str = "efficientnet-b0-malaria.pth"
    SICKLE_MODEL: str = "mobilenetv3-sickle.pth"
    THAL_MODEL: str = "efficientnet-b2-thal.pth"
    SEGMENTOR_TYPE: str = "yolov8"
    DEVICE: str = "cpu"

    MIN_CELLS_FOR_ANALYSIS: int = 50
    MALARIA_POSITIVE_THRESHOLD: float = 0.5
    SICKLE_POSITIVE_THRESHOLD: float = 0.05
    THAL_POSITIVE_THRESHOLD: float = 0.10
    GRAD_CAM_MALARIA_THRESHOLD: float = 0.7
    GRAD_CAM_SICKLE_THRESHOLD: float = 0.8

    IMAGE_RETENTION_DAYS: int = 90
    CELL_CROP_RETENTION_DAYS: int = 30
    REPORT_RETENTION_DAYS: int = 365

    RATE_LIMIT_GENERAL: str = "60/minute"
    RATE_LIMIT_UPLOAD: str = "10/hour"
    DAILY_ANALYSIS_QUOTA: int = 50

    ALLOWED_ORIGINS: str = "http://localhost:5173"

    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"

    SENTRY_DSN: str = ""
    PROMETHEUS_ENABLED: bool = True

    VITE_API_URL: str = "http://localhost:8000/api/v1"
    VITE_WS_URL: str = "ws://localhost:8000/ws"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@lru_cache
def get_settings() -> Settings:
    return Settings()