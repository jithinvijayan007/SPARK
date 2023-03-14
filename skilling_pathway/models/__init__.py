from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .form import (
    Mar1,
    Mar2
)
# from .project import MaritalStatus2

# form
__all__ = [
    "Mar1",
    "Mar2",
]
# # project
# __all__ += ["MaritalStatus2"]
