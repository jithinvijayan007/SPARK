import enum
import uuid
from datetime import datetime

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
    Date,
    Text
)
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import ARRAY

from spark.models import Base


# class CourseGrantMaster(Base):
#     __tablename__ = "course_grant_master"

#     id = Column(Integer, primary_key=True)
#     participant_id = Column(UUID, nullable=False)
#     course_name = Column(String(250), nullable=True)
#     course_id = Column(Integer, nullable=False)
#     funder_id = Column(UUID, nullable=True)
#     status = Column(String(25))
#     course_actual_price = Column(String(25), nullable=True)
#     course_offer_price = Column(String(25), nullable=True)
#     is_active = Column(Boolean, default=True)
#     created_by = Column(UUID(as_uuid=True))
#     created_at = Column(DateTime(timezone=True), default=func.now())
#     updated_at = Column(
#         DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
#     )

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(80), nullable=True)
    last_name = Column(String(80), nullable=True)
    password = Column(Text(), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())
    role = Column(String(120), nullable=False)

    def __repr__(self) -> str:
        return 'User>>> {self.username}'
    

class Store(Base):
    __tablename__ = "store"

    id = Column(Integer, primary_key=True)
    store_name = Column(String(80), nullable=False)
    store_address = Column(String(120), nullable=False)
    store_city = Column(String(120), nullable=False)
    image = Column(TEXT, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(
        Integer,
        ForeignKey(
            "user.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    user = relationship("User", backref=backref("user", uselist=False))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )


    def __repr__(self) -> str:
        return 'User>>> {self.store_name}'