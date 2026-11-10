"""
Human-in-the-Loop review queue and verification API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.inspection import (
    InspectionResponse, 
    ReviewDecisionRequest, 
    FlagInspectionRequest
)
from app.schemas.response import ApiResponse
from app.services.review_service import ReviewService
from app.api.routes.inspection import format_inspection_response

router = APIRouter(prefix="/review", tags=["HITL Review Queue"])

@router.get("/queue", response_model=ApiResponse[List[InspectionResponse]])
async def get_review_queue(db: AsyncSession = Depends(get_db)):
    """Retrieves all borderline or high-uncertainty fabric inspections requiring QA sign-off."""
    flagged_items = await ReviewService.get_pending_review_queue(db)
    formatted = [format_inspection_response(i) for i in flagged_items]
    return ApiResponse(
        success=True,
        message=f"{len(formatted)} items in review queue",
        data=formatted
    )

@router.post("/{inspection_id}/flag", response_model=ApiResponse[InspectionResponse])
async def flag_inspection_for_review(
    inspection_id: str,
    payload: Optional[FlagInspectionRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """Manually routes an inspection to the Human-in-the-Loop review queue."""
    reason = payload.reason if payload else "Manual QA Review Flag"
    updated = await ReviewService.flag_inspection(db, inspection_id, reason=reason)
    if not updated:
        raise HTTPException(status_code=404, detail="Inspection not found")

    return ApiResponse(
        success=True,
        message="Inspection routed to Review Queue successfully",
        data=format_inspection_response(updated)
    )

@router.post("/{inspection_id}/unflag", response_model=ApiResponse[InspectionResponse])
async def unflag_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Removes an inspection from the review queue."""
    updated = await ReviewService.unflag_inspection(db, inspection_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Inspection not found")

    return ApiResponse(
        success=True,
        message="Inspection removed from Review Queue",
        data=format_inspection_response(updated)
    )

@router.post("/{inspection_id}/decision", response_model=ApiResponse[InspectionResponse])
async def submit_review_decision(
    inspection_id: str,
    payload: ReviewDecisionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits inspector approval, rejection (false alarm), or modified annotations.
    Persists decision and marks inspection as resolved.
    """
    updated_inspection = await ReviewService.submit_review_decision(db, inspection_id, payload)
    if not updated_inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    return ApiResponse(
        success=True,
        message=f"Review decision '{payload.action}' recorded successfully",
        data=format_inspection_response(updated_inspection)
    )

@router.post("/seed-demo", response_model=ApiResponse[dict])
async def seed_demo_queue(db: AsyncSession = Depends(get_db)):
    """Seeds or flags available inspection records into the review queue for QA testing."""
    count = await ReviewService.seed_demo_queue(db)
    return ApiResponse(
        success=True,
        message=f"Flagged {count} fabric swatches for QA review",
        data={"flagged_count": count}
    )
