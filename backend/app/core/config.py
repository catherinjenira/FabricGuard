"""
FabricGuard-AI Configuration Settings.
"""

from typing import List, Union
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "FabricGuard-AI"
    API_V1_STR: str = "/api"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./fabricguard.db"

    # Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = Path("./storage/uploads")
    RESULTS_DIR: Path = Path("./storage/results")

    # ML & Detection
    MODEL_WEIGHTS_PATH: str = "../ml/weights/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.50
    UNCERTAINTY_THRESHOLD: float = 0.35
    MAX_IMAGE_SIZE_MB: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def init_storage(self):
        """Ensures storage directories exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.init_storage()

