from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    user_type: str
    employee_id: Optional[str] = None
    student_id: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Class schemas
class ClassBase(BaseModel):
    class_code: str
    class_name: str
    semester: str
    academic_year: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    lecturer_id: int

class ClassResponse(ClassBase):
    id: int
    lecturer_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Section schemas
class SectionBase(BaseModel):
    section_name: str
    schedule_time: Optional[str] = None
    schedule_days: Optional[str] = None
    room_number: Optional[str] = None
    max_students: Optional[int] = 50

class SectionCreate(SectionBase):
    class_id: int

class SectionResponse(SectionBase):
    id: int
    class_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Attendance schemas
class AttendanceSessionCreate(BaseModel):
    section_id: int
    session_date: datetime
    session_start_time: datetime
    session_end_time: Optional[datetime] = None

class AttendanceSessionResponse(BaseModel):
    id: int
    section_id: int
    session_date: datetime
    session_start_time: datetime
    session_end_time: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceMarkRequest(BaseModel):
    session_id: int
    student_id: int
    status: str
    confidence_score: Optional[float] = None

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    status: str
    marked_at: datetime
    confidence_score: Optional[float]
    marked_by_lecturer: bool
    
    class Config:
        from_attributes = True

# Face encoding schemas
class FaceEncodingCreate(BaseModel):
    user_id: int
    encoding_data: str
    reference_photo: str
    quality_score: float
    is_primary: bool = False

class FaceEncodingResponse(BaseModel):
    id: int
    user_id: int
    quality_score: float
    is_primary: bool
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int

class TokenData(BaseModel):
    email: Optional[str] = None