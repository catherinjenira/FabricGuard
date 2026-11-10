"""
Human-in-the-Loop review and active learning triage service.
"""

import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.inspection import Inspection, DefectItem, InspectionStatus
from app.models.review import HumanReview, ReviewAction
from app.schemas.inspection import ReviewDecisionRequest

class ReviewService:
    @staticmethod
    async def get_pending_review_queue(db: AsyncSession, limit: int = 50) -> List[Inspection]:
        """Fetches inspections requiring human inspector verification."""
        stmt = (
            select(Inspection)
            .where(Inspection.flagged_for_review == True)
            .options(selectinload(Inspection.defects), selectinload(Inspection.review))
            .order_by(Inspection.uncertainty_score.desc(), Inspection.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def submit_review_decision(
        db: AsyncSession,
        inspection_id: str,
        payload: ReviewDecisionRequest
    ) -> Optional[Inspection]:
        """Applies inspector verification, updates inspection status, and stores review record."""
        stmt = (
            select(Inspection)
            .where(Inspection.id == inspection_id)
            .options(selectinload(Inspection.defects), selectinload(Inspection.review))
        )
        res = await db.execute(stmt)
        inspection = res.scalar_one_or_none()
        if not inspection:
            return None

        # Determine new status based on reviewer action
        if payload.action == ReviewAction.APPROVED.value:
            new_status = InspectionStatus.DEFECT_DETECTED.value if inspection.defect_count > 0 else InspectionStatus.PASS.value
        elif payload.action == ReviewAction.REJECTED.value:
            # Dismissed false alarm
            new_status = InspectionStatus.PASS.value
            inspection.defect_count = 0
        elif payload.action == ReviewAction.MODIFIED.value:
            new_status = InspectionStatus.DEFECT_DETECTED.value
            if payload.corrected_defects is not None:
                inspection.defect_count = len(payload.corrected_defects)
        else:
            new_status = inspection.status

        inspection.status = new_status
        inspection.flagged_for_review = False

        # Create or update HumanReview
        corrected_json = json.dumps([d.model_dump() for d in payload.corrected_defects]) if payload.corrected_defects else None
        
        if inspection.review:
            inspection.review.action = payload.action
            inspection.review.reviewer_name = payload.reviewer_name
            inspection.review.notes = payload.notes
            inspection.review.corrected_annotations = corrected_json
        else:
            review = HumanReview(
                inspection_id=inspection.id,
                reviewer_name=payload.reviewer_name,
                action=payload.action,
                notes=payload.notes,
                corrected_annotations=corrected_json
            )
            db.add(review)

        await db.commit()
        await db.refresh(inspection)
        return inspection

