"""Configuration package - Model and Database settings."""
from .model import MODEL_NAME
from .database import DB_PATH, PROJECT_ROOT

__all__ = ["MODEL_NAME", "DB_PATH", "PROJECT_ROOT"]
