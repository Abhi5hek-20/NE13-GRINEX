from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import json

from ..models import (
    get_db, User, Enrollment, AttendanceRecord, AttendanceSession, FaceEncoding,
    AttendanceRecordResponse, FaceEncodingCreate, FaceEncodingResponse
)
from ..utils.auth import get_current_student
from ..services import FaceRecognitionService

router = APIRouter()
face_service = FaceRecognitionService()

@router.get("/attendance/my-records", response_model=List[AttendanceRecordResponse])
async def get_my_attendance(
    current_user = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get attendance records for the current student."""
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == current_user.id
    ).all()
    return records

@router.get("/classes")
async def get_my_classes(
    current_user = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get classes enrolled by the current student."""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.is_active == True
    ).all()
    
    classes_data = []
    for enrollment in enrollments:
        class_info = {
            "enrollment_id": enrollment.id,
            "class_id": enrollment.class_id,
            "section_id": enrollment.section_id,
            "class": enrollment.class_obj,
            "section": enrollment.section
        }
        classes_data.append(class_info)
    
    return classes_data

@router.post("/face/register", response_model=FaceEncodingResponse)
async def register_face(
    photo: UploadFile = File(...),
    current_user = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Register face encoding for the current student."""
    # Verify valid image file
    if not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Save uploaded photo
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    photo_path = face_service.save_face_image(photo.file, current_user.id, upload_dir)
    
    # Process face
    face_data = face_service.process_face_image(photo_path)
    
    if not face_data:
        # Remove the failed upload
        if os.path.exists(photo_path):
            os.remove(photo_path)
        raise HTTPException(
            status_code=400,
            detail="No clear face detected in the image. Please upload a clear photo with your face visible."
        )
    
    # Check if student already has a primary face encoding
    existing_primary = db.query(FaceEncoding).filter(
        FaceEncoding.user_id == current_user.id,
        FaceEncoding.is_primary == True,
        FaceEncoding.is_active == True
    ).first()
    
    # Create face encoding record
    face_encoding = FaceEncoding(
        user_id=current_user.id,
        encoding_data=json.dumps(face_data['encoding']),
        reference_photo=photo_path,
        quality_score=face_data['quality'],
        is_primary=not bool(existing_primary)  # Set as primary if no existing primary
    )
    
    db.add(face_encoding)
    db.commit()
    db.refresh(face_encoding)
    
    return face_encoding

@router.get("/face/encodings", response_model=List[FaceEncodingResponse])
async def get_my_face_encodings(
    current_user = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get face encodings for the current student."""
    encodings = db.query(FaceEncoding).filter(
        FaceEncoding.user_id == current_user.id,
        FaceEncoding.is_active == True
    ).all()
    return encodings

@router.post("/attendance/mark-self")
async def mark_self_attendance(
    session_id: int,
    photo: UploadFile = File(...),
    current_user = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Mark attendance for self using photo verification."""
    # Verify valid image file
    if not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Check if student is enrolled in the session's section
    session = db.query(AttendanceSession).filter(
        AttendanceSession.id == session_id,
        AttendanceSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or inactive"
        )
    
    # Verify enrollment
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.section_id == session.section_id,
        Enrollment.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this section"
        )
    
    # Check if attendance already marked
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id,
        AttendanceRecord.student_id == current_user.id
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked for this session"
        )
    
    # Save uploaded photo
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    photo_path = face_service.save_face_image(photo.file, current_user.id, upload_dir)
    
    # Get student's face encodings
    face_encodings = db.query(FaceEncoding).filter(
        FaceEncoding.user_id == current_user.id,
        FaceEncoding.is_active == True
    ).all()
    
    if not face_encodings:
        raise HTTPException(
            status_code=400,
            detail="No face encoding found. Please register your face first."
        )
    
    known_encodings = [
        {"user_id": enc.user_id, "encoding_data": enc.encoding_data}
        for enc in face_encodings
    ]
    
    # Verify face
    verification_result = face_service.verify_face_for_attendance(photo_path, known_encodings)
    
    if verification_result['success'] and verification_result['user_id'] == current_user.id:
        # Create attendance record
        db_record = AttendanceRecord(
            session_id=session_id,
            student_id=current_user.id,
            status="present",
            verification_photo=photo_path,
            confidence_score=verification_result['confidence'],
            marked_by_lecturer=False
        )
        db.add(db_record)
        db.commit()
        
        return {
            "message": "Attendance marked successfully",
            "confidence": verification_result['confidence'],
            "quality_score": verification_result.get('quality_score')
        }
    else:
        # Remove the uploaded photo since verification failed
        if os.path.exists(photo_path):
            os.remove(photo_path)
        
        return {
            "message": "Face verification failed",
            "error": verification_result.get('error', 'Face not recognized'),
            "quality_passed": verification_result.get('quality_passed', False)
        }