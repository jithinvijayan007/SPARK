from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .auth import (
    User
)

# course
__all__ = [
    "User"
    
]

__all__ += [
]
