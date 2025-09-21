# Routes package initialization
from .auth import router as auth_router
from .lecturer import router as lecturer_router  
from .student import router as student_router

__all__ = ["auth_router", "lecturer_router", "student_router"]