"""
FabricGuard-AI Configuration Settings.
Supports MySQL database connection with connection pooling and cloud deployment support.
"""

import os
from typing import List, Optional
from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FabricGuard-AI"
    API_V1_STR: str = "/api"
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    # MySQL Database Configuration
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "Catherin@07"
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "fabricguard_db"
    DATABASE_URL: Optional[str] = None

    # Storage (Anchored to backend base directory)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage"
    UPLOAD_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage" / "uploads"
    RESULTS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "storage" / "results"

    # ML & Detection
    MODEL_WEIGHTS_PATH: str = "../ml/weights/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.25
    UNCERTAINTY_THRESHOLD: float = 0.35
    MAX_IMAGE_SIZE_MB: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_database_url(self) -> str:
        """Constructs safe MySQL async database URL or uses explicit DATABASE_URL."""
        if self.DATABASE_URL:
            # If standard mysql:// is provided, convert to async driver mysql+aiomysql://
            if self.DATABASE_URL.startswith("mysql://"):
                return self.DATABASE_URL.replace("mysql://", "mysql+aiomysql://", 1)
            return self.DATABASE_URL

        # Escape special characters in password
        encoded_pwd = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+aiomysql://{self.MYSQL_USER}:{encoded_pwd}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    def init_storage(self):
        """Ensures storage directories exist."""
        if os.environ.get("VERCEL"):
            self.STORAGE_DIR = Path("/tmp/storage")
            self.UPLOAD_DIR = Path("/tmp/storage/uploads")
            self.RESULTS_DIR = Path("/tmp/storage/results")
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.init_storage()
