"""
SQLAlchemy ORM models for Human-in-the-Loop (HITL) QA Review.
"""

import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

class ReviewAction(str, enum.Enum):
    APPROVED = "APPROVED"       # Inspector agreed with AI detection
    REJECTED = "REJECTED"       # Inspector dismissed false positive
    MODIFIED = "MODIFIED"       # Inspector edited bounding box or label

class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id = Column(String(36), ForeignKey("inspections.id"), nullable=False, unique=True)
    reviewer_name = Column(String(100), default="QA Inspector")
    action = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    corrected_annotations = Column(Text, nullable=True) # JSON serialized corrected boxes
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    inspection = relationship("Inspection", back_populates="review")

