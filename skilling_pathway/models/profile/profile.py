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


# choices

class HighestEducation(enum.Enum):
    HIGH_SCHOOL = "High School"
    GRADUATE = "Graduate"
    POST_GRADUATE = "Post Graduate"
    DOCTORATE = "Doctorate"


class EnglishSpeakingLevel(enum.Enum):
    BASIC = "Basic"
    INTERMEDIATE = "Intermediate"
    FLUENT = "Fluent"
    NO_ENGLISH = "No English"


class EmploymentType(enum.Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"


class WorkPlaceType(enum.Enum):
    OFFICE = "Office"
    WORK_FROM_HOME = "Work From Home"
    WORK_FROM_FIELD = "Work From Field"


class ParticipantProfile(Base):
    __tablename__ = "participant_profile"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    participant_id = Column(UUID, nullable=True)
    participant_user_id = Column(UUID, nullable=True)

    highest_education = Column(String, nullable=True)
    english_speaking_level = Column(Enum(EnglishSpeakingLevel), nullable=True)
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
    preferred_employment_type = Column(Enum(EmploymentType), nullable=True)
    preferred_work_place_type = Column(Enum(WorkPlaceType), nullable=True)
    preferred_job_role = Column(ARRAY(String), nullable=True)

    profile_score = relationship("ProfileScore", back_populates="participant_profile")


class ProfileScore(Base):
    __tablename__ = "profile_score"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    participant_id = Column(UUID, nullable=True)
    participant_user_id = Column(UUID, nullable=True)
    participant_profile_id = Column(UUID, nullable=True)
    participant_profile = relationship("ParticipantProfile", back_populates="profile_score")
    score = Column(Float, nullable=True)
