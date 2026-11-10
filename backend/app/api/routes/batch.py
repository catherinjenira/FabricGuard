"""
Batch fabric inspection API endpoints.
"""

import io
import uuid
import base64
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from PIL import Image

from app.core.config import settings
from app.core.database import get_db
from app.models.inspection import BatchInspection, Inspection, DefectItem, InspectionStatus
from app.schemas.inspection import BatchResponse, InspectionResponse
from app.schemas.response import ApiResponse
from app.services.inference import inference_engine
from app.services.image_processing import apply_clahe, save_processed_image
from app.utils.file_validation import validate_image_file, sanitize_filename
from app.utils.image_utils import draw_defect_boxes
from app.api.routes.inspection import format_inspection_response

router = APIRouter(prefix="/batch", tags=["Batch Inspection"])

@router.post("/upload", response_model=ApiResponse[BatchResponse])
async def process_batch_inspection(
    files: List[UploadFile] = File(...),
    batch_name: str = Form("Roll Batch"),
    fabric_type: str = Form("cotton_weave"),
    enhance_clahe: bool = Form(True),
    confidence_threshold: float = Form(0.50),
    db: AsyncSession = Depends(get_db)
):
    """Processes a bulk upload of fabric inspection images."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for batch processing")

    batch_id = str(uuid.uuid4())
    batch = BatchInspection(
        id=batch_id,
        batch_name=batch_name,
        total_images=len(files),
        passed_count=0,
        defect_count=0,
        flagged_count=0
    )
    db.add(batch)

    inspections_list = []
    
    for file in files:
        content = await validate_image_file(file, max_size_mb=settings.MAX_IMAGE_SIZE_MB)
        safe_name = sanitize_filename(file.filename or "fabric.jpg")
        file_id = str(uuid.uuid4())
        
        upload_path = settings.UPLOAD_DIR / f"{file_id}_{safe_name}"
        annotated_path = settings.RESULTS_DIR / f"annotated_{file_id}_{safe_name}"

        image = Image.open(io.BytesIO(content)).convert("RGB")
        save_processed_image(image, upload_path)

        processed_img = apply_clahe(image) if enhance_clahe else image
        detections, latency_ms, max_u, is_flagged, model_annotated = inference_engine.predict(
            processed_img, conf_threshold=confidence_threshold
        )

        annotated_img = model_annotated if model_annotated else draw_defect_boxes(image, detections)
        save_processed_image(annotated_img, annotated_path)

        # Base64 serialization for permanent MySQL persistence
        img_b64 = "data:image/jpeg;base64," + base64.b64encode(content).decode()
        buf = io.BytesIO()
        annotated_img.save(buf, format="JPEG", quality=90)
        ann_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

        # Mirror to root storage for instant Desktop Explorer visibility
        try:
            root_upload = Path("../storage/uploads") / f"{file_id}_{safe_name}"
            root_results = Path("../storage/results") / f"annotated_{file_id}_{safe_name}"
            save_processed_image(image, root_upload)
            save_processed_image(annotated_img, root_results)
        except Exception:
            pass

        # Every checked item in the batch automatically routes to Review Queue
        status = InspectionStatus.FLAGGED_FOR_REVIEW.value
        batch.flagged_count += 1
        if len(detections) > 0:
            batch.defect_count += 1
        else:
            batch.passed_count += 1

        inspection = Inspection(
            id=file_id,
            batch_id=batch_id,
            filename=safe_name,
            image_path=str(upload_path),
            annotated_path=str(annotated_path),
            image_base64=img_b64,
            annotated_base64=ann_b64,
            status=status,
            defect_count=len(detections),
            max_confidence=max([d["confidence"] for d in detections], default=1.0 if not detections else 0.0),
            uncertainty_score=max_u,
            flagged_for_review=True,
            inference_time_ms=latency_ms,
            fabric_type=fabric_type
        )

        for det in detections:
            box = det["box"]
            item = DefectItem(
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
            inspection.defects.append(item)

        db.add(inspection)
        inspections_list.append(inspection)

    await db.commit()
    await db.refresh(batch)

    # Format response
    formatted_inspections = [format_inspection_response(i) for i in inspections_list]
    batch_resp = BatchResponse(
        id=batch.id,
        batch_name=batch.batch_name,
        total_images=batch.total_images,
        passed_count=batch.passed_count,
        defect_count=batch.defect_count,
        flagged_count=batch.flagged_count,
        created_at=batch.created_at,
        inspections=formatted_inspections
    )

    return ApiResponse(
        success=True,
        message=f"Batch processed. {batch.total_images} fabric swatches analyzed.",
        data=batch_resp
    )

@router.get("/{batch_id}", response_model=ApiResponse[BatchResponse])
async def get_batch_details(batch_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves batch inspection session by ID."""
    stmt = (
        select(BatchInspection)
        .where(BatchInspection.id == batch_id)
        .options(
            selectinload(BatchInspection.inspections).selectinload(Inspection.defects),
            selectinload(BatchInspection.inspections).selectinload(Inspection.review)
        )
    )
    res = await db.execute(stmt)
    batch = res.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch inspection not found")

    formatted_inspections = [format_inspection_response(i) for i in batch.inspections]
    return ApiResponse(
        success=True,
        data=BatchResponse(
            id=batch.id,
            batch_name=batch.batch_name,
            total_images=batch.total_images,
            passed_count=batch.passed_count,
            defect_count=batch.defect_count,
            flagged_count=batch.flagged_count,
            created_at=batch.created_at,
            inspections=formatted_inspections
        )
    )

