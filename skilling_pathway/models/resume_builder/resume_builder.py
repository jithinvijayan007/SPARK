import enum
import uuid

from sqlalchemy import (
    TEXT,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    func,
    Date
)
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import ARRAY
import datetime

from skilling_pathway.models import Base

class ResumeBuilder(Base):
    __tablename__ = "resume_builder"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(TEXT)
    mobile = Column(String(15),nullable=True)
    email  = Column(String(30),nullable=True)
    gender = Column(String(5),nullable=True)
    current_address = Column(TEXT, nullable=True)
    education_qualification = Column(ARRAY(String), nullable=True)
    skills = Column(ARRAY(String), nullable=True)
    work_experience = Column(JSON,nullable=True)
    certification = Column(ARRAY(UUID),nullable=True)
    # other_certifications = Column(JSON,nullable=True)
    is_active = Column(Boolean,default=True)
    created_by = Column(UUID, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)