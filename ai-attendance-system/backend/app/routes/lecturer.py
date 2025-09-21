from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from ..models import (
    get_db, User, Class, Section, Enrollment, AttendanceSession, AttendanceRecord, FaceEncoding,
    ClassCreate, ClassResponse, SectionCreate, SectionResponse,
    AttendanceSessionCreate, AttendanceSessionResponse,
    AttendanceMarkRequest, AttendanceRecordResponse
)
from ..utils.auth import get_current_lecturer, get_current_active_user
from ..services import FaceRecognitionService

router = APIRouter()
face_service = FaceRecognitionService()

@router.get("/classes", response_model=List[ClassResponse])
async def get_lecturer_classes(
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get all classes for the current lecturer."""
    classes = db.query(Class).filter(
        Class.lecturer_id == current_user.id,
        Class.is_active == True
    ).all()
    return classes

@router.post("/classes", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Create a new class."""
    # Verify lecturer is creating their own class
    if class_data.lecturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create classes for yourself"
        )
    
    # Check if class code already exists
    existing_class = db.query(Class).filter(Class.class_code == class_data.class_code).first()
    if existing_class:
        raise HTTPException(
            status_code=400,
            detail="Class code already exists"
        )
    
    db_class = Class(**class_data.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/classes/{class_id}/sections", response_model=List[SectionResponse])
async def get_class_sections(
    class_id: int,
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get all sections for a specific class."""
    # Verify lecturer owns the class
    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.lecturer_id == current_user.id
    ).first()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or not authorized"
        )
    
    sections = db.query(Section).filter(
        Section.class_id == class_id,
        Section.is_active == True
    ).all()
    return sections

@router.post("/sections", response_model=SectionResponse)
async def create_section(
    section_data: SectionCreate,
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Create a new section for a class."""
    # Verify lecturer owns the class
    class_obj = db.query(Class).filter(
        Class.id == section_data.class_id,
        Class.lecturer_id == current_user.id
    ).first()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or not authorized"
        )
    
    db_section = Section(**section_data.dict())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.post("/attendance/session", response_model=AttendanceSessionResponse)
async def create_attendance_session(
    session_data: AttendanceSessionCreate,
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Create a new attendance session."""
    # Verify lecturer owns the section
    section = db.query(Section).join(Class).filter(
        Section.id == session_data.section_id,
        Class.lecturer_id == current_user.id
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found or not authorized"
        )
    
    db_session = AttendanceSession(
        **session_data.dict(),
        created_by=current_user.id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.post("/attendance/mark")
async def mark_attendance_manual(
    attendance_data: AttendanceMarkRequest,
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Manually mark attendance for a student."""
    # Verify lecturer owns the session
    session = db.query(AttendanceSession).join(Section).join(Class).filter(
        AttendanceSession.id == attendance_data.session_id,
        Class.lecturer_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not authorized"
        )
    
    # Check if attendance already marked
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == attendance_data.session_id,
        AttendanceRecord.student_id == attendance_data.student_id
    ).first()
    
    if existing_record:
        # Update existing record
        existing_record.status = attendance_data.status
        existing_record.marked_by_lecturer = True
        existing_record.confidence_score = attendance_data.confidence_score
    else:
        # Create new record
        db_record = AttendanceRecord(
            session_id=attendance_data.session_id,
            student_id=attendance_data.student_id,
            status=attendance_data.status,
            marked_by_lecturer=True,
            confidence_score=attendance_data.confidence_score
        )
        db.add(db_record)
    
    db.commit()
    return {"message": "Attendance marked successfully"}

@router.post("/attendance/mark-photo")
async def mark_attendance_photo(
    session_id: int,
    photo: UploadFile = File(...),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark attendance using photo verification."""
    # Verify valid image file
    if not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Get session and verify access
    session = db.query(AttendanceSession).join(Section).join(Class).filter(
        AttendanceSession.id == session_id,
        AttendanceSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or inactive"
        )
    
    # Save uploaded photo
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    photo_path = face_service.save_face_image(photo.file, current_user.id, upload_dir)
    
    # Get all face encodings for students in this section
    enrollments = db.query(FaceEncoding).join(User).join(Enrollment).filter(
        Enrollment.section_id == session.section_id,
        Enrollment.is_active == True,
        FaceEncoding.is_active == True,
        User.user_type == "student"
    ).all()
    
    known_encodings = [
        {"user_id": enc.user_id, "encoding_data": enc.encoding_data}
        for enc in enrollments
    ]
    
    # Verify face
    verification_result = face_service.verify_face_for_attendance(photo_path, known_encodings)
    
    if verification_result['success']:
        # Mark attendance
        student_id = verification_result['user_id']
        
        # Check if already marked
        existing_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == student_id
        ).first()
        
        if existing_record:
            return {"message": "Attendance already marked for this session"}
        
        # Create new attendance record
        db_record = AttendanceRecord(
            session_id=session_id,
            student_id=student_id,
            status="present",
            verification_photo=photo_path,
            confidence_score=verification_result['confidence'],
            marked_by_lecturer=False
        )
        db.add(db_record)
        db.commit()
        
        return {
            "message": "Attendance marked successfully",
            "student_id": student_id,
            "confidence": verification_result['confidence']
        }
    else:
        return {
            "message": "Face verification failed",
            "error": verification_result.get('error', 'Unknown error'),
            "quality_passed": verification_result.get('quality_passed', False)
        }

@router.get("/attendance/session/{session_id}/records", response_model=List[AttendanceRecordResponse])
async def get_session_attendance(
    session_id: int,
    current_user = Depends(get_current_lecturer),
    db: Session = Depends(get_db)
):
    """Get attendance records for a specific session."""
    # Verify lecturer owns the session
    session = db.query(AttendanceSession).join(Section).join(Class).filter(
        AttendanceSession.id == session_id,
        Class.lecturer_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not authorized"
        )
    
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id
    ).all()
    return records