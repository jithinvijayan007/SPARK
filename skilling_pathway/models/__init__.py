from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .course import (
    InstitutionMaster,
)
# from .project import MaritalStatus2

# course
__all__ = [
    "InstitutionMaster",
    
]
# # project
# __all__ += ["MaritalStatus2"]
