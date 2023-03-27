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



# class Courses(Base):
#     __tablename__ = "courses"

#     id = Column(
#         UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
#     )
#     fullname = Column(String(250))
#     shortname = Column(String(250))
#     status = Column(String(25))
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime(timezone=True), default=func.now())
#     updated_at = Column(
#         DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
#     )


