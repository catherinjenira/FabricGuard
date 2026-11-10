"""
Human-in-the-Loop review queue and verification API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.inspection import InspectionResponse, ReviewDecisionRequest
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

