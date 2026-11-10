"""
Vercel serverless entrypoint for FabricGuard FastAPI service.
"""
from app.main import app

__all__ = ["app"]
