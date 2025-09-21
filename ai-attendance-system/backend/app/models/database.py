from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User model for both lecturers and students
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # 'lecturer' or 'student'
    employee_id = Column(String, unique=True, index=True)  # For lecturers
    student_id = Column(String, unique=True, index=True)   # For students
    department = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    taught_classes = relationship("Class", back_populates="lecturer")
    enrollments = relationship("Enrollment", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
    face_encodings = relationship("FaceEncoding", back_populates="user")

# Class model
class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    class_code = Column(String, unique=True, index=True, nullable=False)
    class_name = Column(String, nullable=False)
    lecturer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    semester = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lecturer = relationship("User", back_populates="taught_classes")
    sections = relationship("Section", back_populates="class_obj")
    enrollments = relationship("Enrollment", back_populates="class_obj")

# Section model for multiple sections per class
class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    section_name = Column(String, nullable=False)  # e.g., "A", "B", "Morning", "Evening"
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    schedule_time = Column(String)  # e.g., "09:00-10:30"
    schedule_days = Column(String)  # e.g., "Monday,Wednesday,Friday"
    room_number = Column(String)
    max_students = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    class_obj = relationship("Class", back_populates="sections")
    enrollments = relationship("Enrollment", back_populates="section")
    attendance_sessions = relationship("AttendanceSession", back_populates="section")

# Enrollment model to link students to classes and sections
class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    student = relationship("User", back_populates="enrollments")
    class_obj = relationship("Class", back_populates="enrollments")
    section = relationship("Section", back_populates="enrollments")

# Attendance Session model for each class session
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    session_date = Column(DateTime, nullable=False)
    session_start_time = Column(DateTime, nullable=False)
    session_end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    section = relationship("Section", back_populates="attendance_sessions")
    attendance_records = relationship("AttendanceRecord", back_populates="session")

# Attendance Record model
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False)  # 'present', 'absent', 'late'
    marked_at = Column(DateTime, default=datetime.utcnow)
    verification_photo = Column(String)  # Path to the photo used for verification
    confidence_score = Column(Float)  # Face recognition confidence
    marked_by_lecturer = Column(Boolean, default=False)  # Manual override by lecturer
    
    # Relationships
    session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records")

# Face Encoding model to store face recognition data
class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    encoding_data = Column(Text, nullable=False)  # JSON string of face encoding
    reference_photo = Column(String, nullable=False)  # Path to reference photo
    quality_score = Column(Float)  # Face quality score
    is_primary = Column(Boolean, default=False)  # Primary encoding for the user
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="face_encodings")

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)