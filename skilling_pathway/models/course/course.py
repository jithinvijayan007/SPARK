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

from skilling_pathway.models import Base


class InstitutionMaster(Base):
    __tablename__ = "institution_master"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_name = Column(String(250),nullable=False)
    status = Column(String(25))
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )

class CourseCategory(Base):
    __tablename__ = "course_category"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    catogory_name = Column(String(250),nullable=False)
    # course = relationship("CourseMaster",back_populates="course_category")
    status = Column(String(25))
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )

class CourseMaster(Base):
    __tablename__ = "course_master"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name = Column(String(250),nullable=False)
    desctiption = Column(TEXT,nullable=True)
    status = Column(String(25),nullable=True)
    is_active = Column(Boolean, default=True)
    original_price = Column(String(50),nullable=True)
    offer_price = Column(String(50),nullable=True)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "course_category.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    partner_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "course_category.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    language = Column(String(250),nullable=True)
    tags = Column(ARRAY(String(50)), nullable=True)
    duration = Column(Integer, nullable=True)
    number_of_modules = Column(Integer, nullable=True)
    total_points = Column(Integer, nullable=True)
    skills = Column(ARRAY(String(50)), nullable=True)
    # course_module = relationship("CourseModuleMaster",back_populates="course")
    course_content = relationship("ModuleContentMaster",back_populates="course")
    # course_category = relationship("CourseCategory",back_populates="course")
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )

class CourseModuleMaster(Base):
    __tablename__ = "course_module_master"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_name = Column(String(250),nullable=False)
    module_order = Column(Integer, nullable=True)
    course = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "course_master.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    # course = relationship("CourseMaster",back_populates="course_module")
    status = Column(String(25),nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )

class ModuleContentMaster(Base):
    __tablename__ = "course_content_master"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_type = Column(String(250),nullable=True)
    content_order = Column(Integer, nullable=True)
    course = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "course_module_master.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    course = relationship("CourseMaster",back_populates="course_content")
    status = Column(String(25))
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )


class CourseGrantMaster(Base):
    __tablename__ = "course_grant_master"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    participant_id = Column(UUID, nullable=True)
    funder_id = Column(UUID, nullable=True)
    status = Column(String(25))
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )








