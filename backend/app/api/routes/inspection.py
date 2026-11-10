"""
Single image fabric inspection API routes.
"""

import io
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from PIL import Image

from app.core.config import settings
from app.core.database import get_db
from app.models.inspection import Inspection, DefectItem, InspectionStatus
from app.schemas.inspection import InspectionResponse, DefectDetection, BoundingBox
from app.schemas.response import ApiResponse
from app.services.inference import inference_engine
from app.services.image_processing import apply_clahe, save_processed_image
from app.utils.file_validation import validate_image_file, sanitize_filename
from app.utils.image_utils import draw_defect_boxes

router = APIRouter(prefix="/inspection", tags=["Inspection"])

def format_inspection_response(inspection: Inspection) -> InspectionResponse:
    """Helper to convert ORM model to InspectionResponse schema."""
    defects = [
        DefectDetection(
            class_id=d.class_id,
            class_name=d.class_name,
            confidence=d.confidence,
            uncertainty=d.uncertainty,
            severity=d.severity,
            box=BoundingBox(
                xmin=d.box_xmin,
                ymin=d.box_ymin,
                xmax=d.box_xmax,
                ymax=d.box_ymax
            )
        )
        for d in inspection.defects
    ]
    
    # Static mount URL
    image_url = f"/storage/uploads/{Path(inspection.image_path).name}"
    annotated_url = f"/storage/results/{Path(inspection.annotated_path).name}" if inspection.annotated_path else None

    return InspectionResponse(
        id=inspection.id,
        batch_id=inspection.batch_id,
        filename=inspection.filename,
        image_url=image_url,
        annotated_url=annotated_url,
        status=inspection.status,
        defect_count=inspection.defect_count,
        max_confidence=inspection.max_confidence,
        uncertainty_score=inspection.uncertainty_score,
        flagged_for_review=inspection.flagged_for_review,
        inference_time_ms=inspection.inference_time_ms,
        fabric_type=inspection.fabric_type or "cotton_weave",
        created_at=inspection.created_at,
        defects=defects,
        review=inspection.review
    )

@router.post("/single", response_model=ApiResponse[InspectionResponse])
async def inspect_single_image(
    file: UploadFile = File(...),
    fabric_type: str = Form("cotton_weave"),
    enhance_clahe: bool = Form(True),
    confidence_threshold: float = Form(0.50),
    db: AsyncSession = Depends(get_db)
):
    """
    Performs real-time inspection on an uploaded fabric image.
    Applies CLAHE enhancement, YOLO defect detection, and uncertainty evaluation.
    """
    content = await validate_image_file(file, max_size_mb=settings.MAX_IMAGE_SIZE_MB)
    safe_name = sanitize_filename(file.filename or "fabric.jpg")
    file_id = str(uuid.uuid4())
    ext = Path(safe_name).suffix or ".jpg"
    
    upload_path = settings.UPLOAD_DIR / f"{file_id}_{safe_name}"
    annotated_path = settings.RESULTS_DIR / f"annotated_{file_id}_{safe_name}"

    # Load PIL image
    image = Image.open(io.BytesIO(content)).convert("RGB")
    
    # Save original
    save_processed_image(image, upload_path)

    # Preprocessing
    processed_img = apply_clahe(image) if enhance_clahe else image

    # Run AI inference
    detections, latency_ms, max_u, is_flagged = inference_engine.predict(
        processed_img, conf_threshold=confidence_threshold
    )

    # Render bounding boxes onto annotated copy
    annotated_img = draw_defect_boxes(image, detections)
    save_processed_image(annotated_img, annotated_path)

    # Determine status
    if is_flagged:
        status = InspectionStatus.FLAGGED_FOR_REVIEW.value
    elif len(detections) > 0:
        status = InspectionStatus.DEFECT_DETECTED.value
    else:
        status = InspectionStatus.PASS.value

    max_conf = max([d["confidence"] for d in detections], default=1.0 if not detections else 0.0)

    # Persist in DB
    inspection = Inspection(
        id=file_id,
        filename=safe_name,
        image_path=str(upload_path),
        annotated_path=str(annotated_path),
        status=status,
        defect_count=len(detections),
        max_confidence=max_conf,
        uncertainty_score=max_u,
        flagged_for_review=is_flagged,
        inference_time_ms=latency_ms,
        fabric_type=fabric_type
    )

    for det in detections:
        box = det["box"]
        defect_item = DefectItem(
            class_id=det["class_id"],
            class_name=det["class_name"],
            confidence=det["confidence"],
            uncertainty=det["uncertainty"],
            severity=det["severity"],
            box_xmin=box["xmin"],
            box_ymin=box["ymin"],
            box_xmax=box["xmax"],
            box_ymax=box["ymax"]
        )
        inspection.defects.append(defect_item)

    db.add(inspection)
    await db.commit()
    await db.refresh(inspection)

    # Reload with relationships
    stmt = (
        select(Inspection)
        .where(Inspection.id == inspection.id)
        .options(selectinload(Inspection.defects), selectinload(Inspection.review))
    )
    res = await db.execute(stmt)
    full_inspection = res.scalar_one()

    return ApiResponse(
        success=True,
        message=f"Inspection complete. Status: {status}",
        data=format_inspection_response(full_inspection)
    )

@router.get("/{inspection_id}", response_model=ApiResponse[InspectionResponse])
async def get_inspection(inspection_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves single inspection result by ID."""
    stmt = (
        select(Inspection)
        .where(Inspection.id == inspection_id)
        .options(selectinload(Inspection.defects), selectinload(Inspection.review))
    )
    res = await db.execute(stmt)
    inspection = res.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    return ApiResponse(
        success=True,
        data=format_inspection_response(inspection)
    )

