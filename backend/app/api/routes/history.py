"""
Historical inspection audit trail and search API routes.
"""

import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.inspection import Inspection
from app.schemas.inspection import InspectionResponse
from app.schemas.response import ApiResponse, PaginatedResponse
from app.api.routes.inspection import format_inspection_response

router = APIRouter(prefix="/history", tags=["History & Audit"])

@router.get("", response_model=ApiResponse[PaginatedResponse[InspectionResponse]])
async def get_inspection_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    fabric_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves paginated and filtered inspection records."""
    query = select(Inspection)
    count_query = select(func.count(Inspection.id))

    if status:
        query = query.where(Inspection.status == status)
        count_query = count_query.where(Inspection.status == status)

    if fabric_type:
        query = query.where(Inspection.fabric_type == fabric_type)
        count_query = count_query.where(Inspection.fabric_type == fabric_type)

    total_count = (await db.execute(count_query)).scalar() or 0
    total_pages = max(1, (total_count + limit - 1) // limit)

    offset = (page - 1) * limit
    stmt = (
        query.options(selectinload(Inspection.defects), selectinload(Inspection.review))
        .order_by(desc(Inspection.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    inspections = result.scalars().all()

    items = [format_inspection_response(i) for i in inspections]

    return ApiResponse(
        success=True,
        data=PaginatedResponse(
            items=items,
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    )

@router.delete("/{inspection_id}", response_model=ApiResponse[dict])
async def delete_inspection(inspection_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes an inspection record."""
    stmt = select(Inspection).where(Inspection.id == inspection_id)
    res = await db.execute(stmt)
    inspection = res.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")

    await db.delete(inspection)
    await db.commit()
    return ApiResponse(success=True, message=f"Inspection {inspection_id} deleted successfully.")

@router.get("/export/csv")
async def export_history_csv(db: AsyncSession = Depends(get_db)):
    """Exports inspection history as a downloadable CSV report."""
    stmt = (
        select(Inspection)
        .options(selectinload(Inspection.defects))
        .order_by(desc(Inspection.created_at))
    )
    res = await db.execute(stmt)
    inspections = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Inspection ID", "Filename", "Status", "Defect Count",
        "Max Confidence", "Uncertainty Score", "Flagged Review",
        "Inference Time (ms)", "Fabric Type", "Timestamp"
    ])

    for i in inspections:
        writer.writerow([
            i.id, i.filename, i.status, i.defect_count,
            round(i.max_confidence, 4), round(i.uncertainty_score, 4),
            i.flagged_for_review, round(i.inference_time_ms, 2),
            i.fabric_type, i.created_at.isoformat() if i.created_at else ""
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fabric_inspections.csv"}
    )

