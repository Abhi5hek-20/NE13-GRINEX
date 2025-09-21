import os
import json
from typing import List, Tuple, Optional
from datetime import datetime

class MockFaceRecognitionService:
    """Mock face recognition service for development/testing without OpenCV."""
    
    def __init__(self, quality_threshold: float = 0.6, max_face_distance: float = 0.6):
        """
        Initialize the mock face recognition service.
        
        Args:
            quality_threshold: Minimum quality score for face detection
            max_face_distance: Maximum distance for face matching
        """
        self.quality_threshold = quality_threshold
        self.max_face_distance = max_face_distance
        
    def detect_faces(self, image_path: str) -> List[Tuple[tuple, list]]:
        """
        Mock face detection - always returns one face if image exists.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of tuples containing (face_location, mock_encoding)
        """
        try:
            if os.path.exists(image_path):
                # Return a mock face location and encoding
                face_location = (50, 200, 200, 50)  # (top, right, bottom, left)
                mock_encoding = [0.1] * 128  # Simple mock encoding
                return [(face_location, mock_encoding)]
            return []
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def assess_face_quality(self, image_path: str, face_location: tuple) -> float:
        """
        Mock face quality assessment.
        
        Args:
            image_path: Path to the image file
            face_location: Face location coordinates
            
        Returns:
            Quality score between 0 and 1
        """
        # Return a decent quality score for existing files
        if os.path.exists(image_path):
            return 0.8
        return 0.0
    
    def process_face_image(self, image_path: str) -> Optional[dict]:
        """
        Mock face processing.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with face data or None if no suitable face found
        """
        faces_data = self.detect_faces(image_path)
        
        if not faces_data:
            return None
        
        face_location, face_encoding = faces_data[0]  # Take first face
        quality = self.assess_face_quality(image_path, face_location)
        
        if quality >= self.quality_threshold:
            return {
                'encoding': face_encoding,
                'location': face_location,
                'quality': quality
            }
        
        return None
    
    def compare_faces(self, known_encoding: str, test_encoding: list) -> Tuple[bool, float]:
        """
        Mock face comparison.
        
        Args:
            known_encoding: JSON string of known face encoding
            test_encoding: Test face encoding as list
            
        Returns:
            Tuple of (is_match, confidence_score)
        """
        try:
            # For demo purposes, return a match with reasonable confidence
            # In a real scenario, this would do actual face comparison
            confidence = 0.85  # Mock confidence score
            is_match = confidence >= (1 - self.max_face_distance)
            return is_match, confidence
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, 0.0
    
    def verify_face_for_attendance(self, image_path: str, known_encodings: List[dict]) -> Optional[dict]:
        """
        Mock face verification for attendance.
        
        Args:
            image_path: Path to the uploaded image
            known_encodings: List of dictionaries with user_id and encoding_data
            
        Returns:
            Dictionary with verification result
        """
        # Process the uploaded image
        face_data = self.process_face_image(image_path)
        
        if not face_data:
            return {
                'success': False,
                'error': 'No clear face detected in the image',
                'quality_passed': False
            }
        
        # For demo purposes, if there are known encodings, return the first one as a match
        if known_encodings:
            first_user = known_encodings[0]
            return {
                'success': True,
                'user_id': first_user['user_id'],
                'confidence': 0.85,
                'quality_score': face_data['quality'],
                'quality_passed': True
            }
        else:
            return {
                'success': False,
                'error': 'No registered faces found',
                'quality_passed': True,
                'quality_score': face_data['quality']
            }
    
    def save_face_image(self, image_file, user_id: int, upload_dir: str) -> str:
        """
        Save uploaded face image with proper naming convention.
        
        Args:
            image_file: Uploaded image file
            user_id: User ID for naming
            upload_dir: Upload directory path
            
        Returns:
            Path to saved image file
        """
        # Create user-specific directory
        user_dir = os.path.join(upload_dir, "face_images", str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"face_{timestamp}.jpg"
        file_path = os.path.join(user_dir, filename)
        
        # Save image
        with open(file_path, "wb") as buffer:
            buffer.write(image_file.read())
        
        return file_path