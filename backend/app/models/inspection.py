"""
SQLAlchemy ORM models for Inspection, Defect, and Batch sessions.
"""

import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

class InspectionStatus(str, enum.Enum):
    PASS = "PASS"
    DEFECT_DETECTED = "DEFECT_DETECTED"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW"

class BatchInspection(Base):
    __tablename__ = "batch_inspections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_name = Column(String(255), nullable=False)
    total_images = Column(Integer, default=0)
    passed_count = Column(Integer, default=0)
    defect_count = Column(Integer, default=0)
    flagged_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    inspections = relationship("Inspection", back_populates="batch", cascade="all, delete-orphan")

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("batch_inspections.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)
    annotated_path = Column(String(500), nullable=True)
    status = Column(String(50), default=InspectionStatus.PASS.value)
    defect_count = Column(Integer, default=0)
    max_confidence = Column(Float, default=0.0)
    uncertainty_score = Column(Float, default=0.0)
    flagged_for_review = Column(Boolean, default=False)
    inference_time_ms = Column(Float, default=0.0)
    fabric_type = Column(String(100), default="cotton_weave")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    batch = relationship("BatchInspection", back_populates="inspections")
    defects = relationship("DefectItem", back_populates="inspection", cascade="all, delete-orphan")
    review = relationship("HumanReview", back_populates="inspection", uselist=False, cascade="all, delete-orphan")

class DefectItem(Base):
    __tablename__ = "defect_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String(36), ForeignKey("inspections.id"), nullable=False)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, default=0.0)
    severity = Column(String(50), default="medium")
    
    # Normalized Bounding Box [0.0 - 1.0]
    box_xmin = Column(Float, nullable=False)
    box_ymin = Column(Float, nullable=False)
    box_xmax = Column(Float, nullable=False)
    box_ymax = Column(Float, nullable=False)

    inspection = relationship("Inspection", back_populates="defects")

