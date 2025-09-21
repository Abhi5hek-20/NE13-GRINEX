# Make models package importable
from .database import (
    Base, 
    User, 
    Class, 
    Section, 
    Enrollment, 
    AttendanceSession, 
    AttendanceRecord, 
    FaceEncoding,
    get_db,
    create_tables,
    engine
)
from .schemas import (
    UserBase,
    UserCreate,
    UserResponse,
    UserLogin,
    ClassBase,
    ClassCreate,
    ClassResponse,
    SectionBase,
    SectionCreate,
    SectionResponse,
    AttendanceSessionCreate,
    AttendanceSessionResponse,
    AttendanceMarkRequest,
    AttendanceRecordResponse,
    FaceEncodingCreate,
    FaceEncodingResponse,
    Token,
    TokenData
)

__all__ = [
    "Base", "User", "Class", "Section", "Enrollment", "AttendanceSession", 
    "AttendanceRecord", "FaceEncoding", "get_db", "create_tables", "engine",
    "UserBase", "UserCreate", "UserResponse", "UserLogin",
    "ClassBase", "ClassCreate", "ClassResponse",
    "SectionBase", "SectionCreate", "SectionResponse",
    "AttendanceSessionCreate", "AttendanceSessionResponse",
    "AttendanceMarkRequest", "AttendanceRecordResponse",
    "FaceEncodingCreate", "FaceEncodingResponse",
    "Token", "TokenData"
]