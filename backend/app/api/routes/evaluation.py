"""
Model performance, telemetry, and live analytics API endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db
from app.schemas.response import ApiResponse, DashboardStats, ModelMetricsResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Model Evaluation & Telemetry"])

@router.get("/storage-status", response_model=ApiResponse[Dict[str, Any]])
async def get_storage_status(db: AsyncSession = Depends(get_db)):
    """Provides storage verification: MySQL checkings records, disk files, and base64 stats."""
    count_inspections = (await db.execute(text("SELECT count(*) FROM inspections"))).scalar() or 0
    count_b64 = (await db.execute(text("SELECT count(*) FROM inspections WHERE image_base64 IS NOT NULL"))).scalar() or 0
    count_defects = (await db.execute(text("SELECT count(*) FROM defect_items"))).scalar() or 0
    
    upload_files = len(list(settings.UPLOAD_DIR.glob("*"))) if settings.UPLOAD_DIR.exists() else 0
    result_files = len(list(settings.RESULTS_DIR.glob("*"))) if settings.RESULTS_DIR.exists() else 0
    
    return ApiResponse(
        success=True,
        message="Storage mechanism operational",
        data={
            "database": {
                "engine": "MySQL (InnoDB)",
                "database": settings.MYSQL_DB,
                "host": f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}",
                "table_checkings": "Active (`checkings` view & `inspections`)",
                "total_checkings_saved": count_inspections,
                "images_in_mysql_blob": count_b64,
                "defect_items_saved": count_defects
            },
            "disk_storage": {
                "uploads_dir": str(settings.UPLOAD_DIR.resolve()),
                "results_dir": str(settings.RESULTS_DIR.resolve()),
                "total_raw_images": upload_files,
                "total_annotated_images": result_files
            }
        }
    )

@router.get("/metrics", response_model=ApiResponse[ModelMetricsResponse])
async def get_model_evaluation_metrics():
    """Retrieves current YOLO model benchmark accuracy metrics."""
    metrics = EvaluationService.get_model_metrics()
    return ApiResponse(
        success=True,
        data=metrics
    )

@router.get("/stats", response_model=ApiResponse[DashboardStats])
async def get_dashboard_statistics(db: AsyncSession = Depends(get_db)):
    """Retrieves high-level factory throughput and defect rate statistics."""
    stats = await EvaluationService.get_dashboard_stats(db)
    return ApiResponse(
        success=True,
        data=stats
    )

@router.get("/defect-distribution", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_defect_distribution(db: AsyncSession = Depends(get_db)):
    """Returns frequency distribution of detected fabric defect categories."""
    distribution = await EvaluationService.get_defect_distribution(db)
    return ApiResponse(
        success=True,
        data=distribution
    )

