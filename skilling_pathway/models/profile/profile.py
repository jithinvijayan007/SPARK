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
from pymongo import ASCENDING, DESCENDING
from bson.objectid import ObjectId
from skilling_pathway.api.extensions import client

class ParticipantProfile(Base):
    __tablename__ = "participant_profile"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    participant_id = Column(UUID, nullable=True)
    participant_user_id = Column(UUID, nullable=True)
    summary = Column(TEXT, nullable=True)

    highest_education = Column(String, nullable=True)
    english_speaking_level = Column(ARRAY(String), nullable=True)
    other_languages = Column(ARRAY(String), nullable=True)
    current_skills = Column(ARRAY(String), nullable=True)

    interested_course = Column(ARRAY(String), nullable=True)
    preferred_course_language = Column(ARRAY(String), nullable=True)

    current_employment_status = Column(Boolean, nullable=True)
    current_employment_details = Column(TEXT, nullable=True)
    employment_start_date = Column(Date, nullable=True)
    employment_end_date = Column(Date, nullable=True)
    preferred_job_location_state = Column(ARRAY(String), nullable=True)
    preferred_job_location_city = Column(ARRAY(String), nullable=True)
    preferred_employment_type = Column(ARRAY(String), nullable=True)
    preferred_work_place_type = Column(ARRAY(String), nullable=True)
    preferred_job_role = Column(ARRAY(String), nullable=True)
    mobile = Column(String(15),nullable=True)
    email  = Column(String(45),nullable=True)
    gender = Column(String(10),nullable=True)
    address = Column(String, nullable=True)
    certificates = Column(ARRAY(String), nullable=True)
    educational_qualifications = Column(ARRAY(String), nullable=True)
    experience = Column(ARRAY(String), nullable=True)
    resume_added = Column(Boolean, nullable=True, default=False)

    profile_scores = relationship("ProfileScore", back_populates="participant_profile")

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )


class ProfileScore(Base):
    __tablename__ = "profile_score"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    score = Column(Float, nullable=False)
    level = Column(String(10),nullable=True)
    participant_profile_id = Column(UUID(as_uuid=True), ForeignKey("participant_profile.id"))
    participant_id = Column(UUID, nullable=True)
    participant_profile = relationship("ParticipantProfile", back_populates="profile_scores")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), server_onupdate=func.now()
    )


mg_db = client.skilling_pathway

class ParticipantProfileSchema:
    collection = mg_db.participant_profile

    @staticmethod
    def create_index():
        ParticipantProfileSchema.collection.create_index([('id', ASCENDING)], unique=True)

    @staticmethod
    def from_dict(data):
        return {
            'id': ObjectId(),
            'participant_id': data.get('participant_id'),
            'participant_user_id': data.get('participant_user_id'),
            'highest_education': data.get('highest_education'),
            'english_speaking_level': data.get('english_speaking_level'),
            'other_languages': data.get('other_languages'),
            'current_skills': data.get('current_skills'),
            'interested_course': data.get('interested_course'),
            'preferred_course_language': data.get('preferred_course_language'),
            'current_employment_status': data.get('current_employment_status'),
            'current_employment_details': data.get('current_employment_details'),
            'employment_start_date': data.get('employment_start_date'),
            'employment_end_date': data.get('employment_end_date'),
            'preferred_job_location_state': data.get('preferred_job_location_state'),
            'preferred_job_location_city': data.get('preferred_job_location_city'),
            'preferred_employment_type': data.get('preferred_employment_type'),
            'preferred_work_place_type': data.get('preferred_work_place_type'),
            'preferred_job_role': data.get('preferred_job_role')
        }
