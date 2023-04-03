from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .course import (
    InstitutionMaster,
    CourseCategory,
   CourseMaster,
   CourseModuleMaster,
   ModuleContentMaster,
   CourseGrantMaster
)

from .profile import (
    ParticipantProfile,
    ProfileScore
)
# from .project import MaritalStatus2

# course
__all__ = [
    "InstitutionMaster",
    "CourseCategory",
    "CourseMaster",
    "CourseModuleMaster",
    "ModuleContentMaster",
    "CourseGrantMaster"
    
]
# # project
# __all__ += ["MaritalStatus2"]

__all__ += [
    "ParticipantProfile",
    "ProfileScore"
]
