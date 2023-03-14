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



class Mar1(Base):
    __tablename__ = "mar1"

    marital_status_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    status = Column(String(25))
    yes_bank_text = Column(String(10))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )
    sorting_order = Column(Integer, nullable=True)
    default_list = Column(Boolean, default=True)
    system_text = Column(String(100))
    is_active = Column(Boolean, default=True)


class Mar2(Base):
    __tablename__ = "mar2"

    marital_status_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    status = Column(String(25))
    yes_bank_text = Column(String(10))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )
    sorting_order = Column(Integer, nullable=True)
    default_list = Column(Boolean, default=True)
    system_text = Column(String(100))
    is_active = Column(Boolean, default=True)