"""
Model performance, telemetry, and live analytics API endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.response import ApiResponse, DashboardStats, ModelMetricsResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Model Evaluation & Telemetry"])

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

