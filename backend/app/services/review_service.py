"""
Human-in-the-Loop review and active learning triage service.
"""

import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
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
    async def flag_inspection(
        db: AsyncSession,
        inspection_id: str,
        reason: Optional[str] = "Manual QA Review Flag"
    ) -> Optional[Inspection]:
        """Flags an inspection for HITL review queue."""
        stmt = (
            select(Inspection)
            .where(Inspection.id == inspection_id)
            .options(selectinload(Inspection.defects), selectinload(Inspection.review))
        )
        res = await db.execute(stmt)
        inspection = res.scalar_one_or_none()
        if not inspection:
            return None

        inspection.flagged_for_review = True
        inspection.status = InspectionStatus.FLAGGED_FOR_REVIEW.value
        
        if reason:
            if inspection.review:
                inspection.review.notes = f"Flagged: {reason}"
            else:
                review = HumanReview(
                    inspection_id=inspection.id,
                    reviewer_name="Inspector",
                    action="FLAGGED",
                    notes=f"Flagged: {reason}"
                )
                db.add(review)

        await db.commit()
        await db.refresh(inspection)
        return inspection

    @staticmethod
    async def unflag_inspection(db: AsyncSession, inspection_id: str) -> Optional[Inspection]:
        """Removes an inspection from the review queue without submitting full review."""
        stmt = (
            select(Inspection)
            .where(Inspection.id == inspection_id)
            .options(selectinload(Inspection.defects), selectinload(Inspection.review))
        )
        res = await db.execute(stmt)
        inspection = res.scalar_one_or_none()
        if not inspection:
            return None

        inspection.flagged_for_review = False
        inspection.status = (
            InspectionStatus.DEFECT_DETECTED.value 
            if inspection.defect_count > 0 
            else InspectionStatus.PASS.value
        )
        await db.commit()
        await db.refresh(inspection)
        return inspection

    @staticmethod
    async def submit_review_decision(
        db: AsyncSession,
        inspection_id: str,
        payload: ReviewDecisionRequest
    ) -> Optional[Inspection]:
        """
        Applies inspector verification:
        - APPROVED: confirms defect presence, resolves queue
        - REJECTED: marks false alarm, clears defects, sets PASS
        - MODIFIED: updates defect items in DB with inspector's corrections
        """
        stmt = (
            select(Inspection)
            .where(Inspection.id == inspection_id)
            .options(selectinload(Inspection.defects), selectinload(Inspection.review))
        )
        res = await db.execute(stmt)
        inspection = res.scalar_one_or_none()
        if not inspection:
            return None

        # Determine new status & update defects based on reviewer action
        if payload.action == ReviewAction.APPROVED.value:
            new_status = (
                InspectionStatus.DEFECT_DETECTED.value 
                if inspection.defect_count > 0 
                else InspectionStatus.PASS.value
            )
        elif payload.action == ReviewAction.REJECTED.value:
            # Dismissed false alarm -> clear defect records from DB
            new_status = InspectionStatus.PASS.value
            inspection.defects.clear()
            inspection.defect_count = 0
            inspection.uncertainty_score = 0.0
        elif payload.action == ReviewAction.MODIFIED.value:
            # Reclassified or updated annotations -> update defect items
            if payload.corrected_defects is not None:
                inspection.defects.clear()
                for d in payload.corrected_defects:
                    box = d.box
                    inspection.defects.append(DefectItem(
                        class_id=d.class_id,
                        class_name=d.class_name,
                        confidence=d.confidence,
                        uncertainty=d.uncertainty,
                        severity=d.severity,
                        box_xmin=box.xmin,
                        box_ymin=box.ymin,
                        box_xmax=box.xmax,
                        box_ymax=box.ymax
                    ))
                inspection.defect_count = len(payload.corrected_defects)
            new_status = (
                InspectionStatus.DEFECT_DETECTED.value 
                if inspection.defect_count > 0 
                else InspectionStatus.PASS.value
            )
        else:
            new_status = inspection.status

        inspection.status = new_status
        inspection.flagged_for_review = False

        # Create or update HumanReview record
        corrected_json = (
            json.dumps([d.model_dump() for d in payload.corrected_defects]) 
            if payload.corrected_defects 
            else None
        )
        
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

    @staticmethod
    async def seed_demo_queue(db: AsyncSession) -> int:
        """
        Flags existing defect inspections or borderline samples to ensure the review queue
        is populated and functional for demonstration/testing.
        """
        stmt = (
            select(Inspection)
            .where(or_(Inspection.defect_count > 0, Inspection.uncertainty_score > 0.10))
            .limit(10)
        )
        res = await db.execute(stmt)
        items = list(res.scalars().all())
        
        flagged_count = 0
        for item in items:
            item.flagged_for_review = True
            item.status = InspectionStatus.FLAGGED_FOR_REVIEW.value
            flagged_count += 1
            
        await db.commit()
        return flagged_count
