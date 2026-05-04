from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "LokiVision"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ML Model settings
    MODEL_DIR: str = "/app/models"
    SEGMENTOR_MODEL: str = "yolov8n-blood.pt"
    MALARIA_MODEL: str = "efficientnet-b0-malaria.pth"
    SICKLE_MODEL: str = "mobilenetv3-sickle.pth"
    THAL_MODEL: str = "efficientnet-b2-thal.pth"
    SEGMENTOR_TYPE: str = "yolov8"
    DEVICE: str = "cpu"

    # Thresholds
    MIN_CELLS_FOR_ANALYSIS: int = 50
    MALARIA_POSITIVE_THRESHOLD: float = 0.5
    SICKLE_POSITIVE_THRESHOLD: float = 0.05
    THAL_POSITIVE_THRESHOLD: float = 0.10
    GRAD_CAM_MALARIA_THRESHOLD: float = 0.7
    GRAD_CAM_SICKLE_THRESHOLD: float = 0.8

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@lru_cache
def get_settings() -> Settings:
    return Settings()