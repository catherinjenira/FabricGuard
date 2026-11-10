"""
Standardized API envelope and statistics schemas.
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int

class DashboardStats(BaseModel):
    total_inspections: int
    passed_rolls: int
    defect_rolls: int
    pending_reviews: int
    overall_pass_rate: float
    avg_inference_latency_ms: float
    active_model_version: str = "FabricGuard-YOLOv8s-v1.4"

class DefectClassMetric(BaseModel):
    id: int
    name: str
    precision: float
    recall: float
    mAP50: float
    f1: float
    support: int

class ModelMetricsResponse(BaseModel):
    model_name: str
    version: str
    mAP50: float
    mAP50_95: float
    precision: float
    recall: float
    f1_score: float
    avg_inference_latency_ms: float
    per_class: List[DefectClassMetric]
    drift_status: str = "STABLE"

