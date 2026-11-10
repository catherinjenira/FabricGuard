"""
Pydantic schemas for Defect Inspection and HITL Review.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    xmin: float = Field(..., ge=0.0, le=1.0, description="Normalized x min")
    ymin: float = Field(..., ge=0.0, le=1.0, description="Normalized y min")
    xmax: float = Field(..., ge=0.0, le=1.0, description="Normalized x max")
    ymax: float = Field(..., ge=0.0, le=1.0, description="Normalized y max")

class DefectDetection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    uncertainty: float = 0.0
    severity: str = "medium"
    box: BoundingBox

class ReviewSummary(BaseModel):
    id: str
    reviewer_name: str
    action: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InspectionResponse(BaseModel):
    id: str
    batch_id: Optional[str] = None
    filename: str
    image_url: str
    annotated_url: Optional[str] = None
    status: str
    defect_count: int
    max_confidence: float
    uncertainty_score: float
    flagged_for_review: bool
    inference_time_ms: float
    fabric_type: str = "cotton_weave"
    created_at: datetime
    defects: List[DefectDetection] = []
    review: Optional[ReviewSummary] = None

    class Config:
        from_attributes = True

class BatchResponse(BaseModel):
    id: str
    batch_name: str
    total_images: int
    passed_count: int
    defect_count: int
    flagged_count: int
    created_at: datetime
    inspections: List[InspectionResponse] = []

    class Config:
        from_attributes = True

class ReviewDecisionRequest(BaseModel):
    reviewer_name: str = "Inspector"
    action: str = Field(..., description="APPROVED, REJECTED, or MODIFIED")
    notes: Optional[str] = None
    corrected_defects: Optional[List[DefectDetection]] = None

class FlagInspectionRequest(BaseModel):
    reason: Optional[str] = "Manual QA Review Flag"

