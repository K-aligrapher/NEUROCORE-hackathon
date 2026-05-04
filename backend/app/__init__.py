# app/__init__.py
from app.config import get_settings

settings = get_settings()

__version__ = "1.0.0"
__app_name__ = settings.APP_NAME