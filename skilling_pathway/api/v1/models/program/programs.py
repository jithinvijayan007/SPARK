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

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  


class ProjectDetailMaster(Base):
    __tablename__ = "project_detail_master"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    project_name = Column(String(255),nullable=False)
    program_name = Column(String(255),nullable=True)
    entity = Column(ARRAY(UUID), nullable=True)
    project_description = Column(TEXT, nullable=False)
    project_tagline = Column(TEXT, nullable=True)
    primary_area_of_focus = Column(ARRAY(String(50)), nullable=False)
    primary_participants = Column(ARRAY(String(50)), nullable=False)
    # success_matrix = Column(ARRAY(UUID), nullable=False)
    project_keywords = Column(TEXT, nullable=True)    
    project_timeline = Column(Integer, nullable=False)
    program_start_date = Column(Date, nullable=True)
    program_end_date = Column(Date, nullable=True)
    instrument = Column(ARRAY(UUID), nullable=True)
    project_outputs = Column(TEXT, nullable=False)
    impact_generated = Column(TEXT, nullable=False)
    outcomes = Column(String(200),nullable=False)
    location_coverage_state = Column(ARRAY(String(50)), nullable=False)
    location_coverage_district = Column(ARRAY(String(50)), nullable=True)
    location_coverage_city = Column(String(200),nullable=True)
    events = Column(ARRAY(UUID), nullable=True)    
    program_profile_image = Column(TEXT, nullable=True)
    program_cover_image = Column(TEXT, nullable=True)
    is_active = Column(Boolean, default=True)    
    key_intervention = Column(ARRAY(UUID), nullable=True)    
    sub_intervention = Column(ARRAY(UUID), nullable=True)    
    created_by = Column(type_=UUID(as_uuid=True))
    updated_by = Column(type_=UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), 
        server_onupdate=func.now()
    )







