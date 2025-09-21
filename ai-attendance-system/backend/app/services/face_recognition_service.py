import cv2
import face_recognition
import numpy as np
import json
from typing import List, Tuple, Optional
from PIL import Image
import os
from datetime import datetime

class FaceRecognitionService:
    """Service for face detection, encoding, and recognition operations."""
    
    def __init__(self, quality_threshold: float = 0.6, max_face_distance: float = 0.6):
        """
        Initialize the face recognition service.
        
        Args:
            quality_threshold: Minimum quality score for face detection
            max_face_distance: Maximum distance for face matching
        """
        self.quality_threshold = quality_threshold
        self.max_face_distance = max_face_distance
        
    def detect_faces(self, image_path: str) -> List[Tuple[tuple, np.ndarray]]:
        """
        Detect faces in an image and return face locations and encodings.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of tuples containing (face_location, face_encoding)
        """
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return []
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return list(zip(face_locations, face_encodings))
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def assess_face_quality(self, image_path: str, face_location: tuple) -> float:
        """
        Assess the quality of a detected face.
        
        Args:
            image_path: Path to the image file
            face_location: Face location coordinates (top, right, bottom, left)
            
        Returns:
            Quality score between 0 and 1
        """
        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return 0.0
            
            top, right, bottom, left = face_location
            
            # Extract face region
            face_region = image[top:bottom, left:right]
            
            # Convert to grayscale for analysis
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Calculate quality metrics
            quality_score = 0.0
            
            # 1. Face size check (larger faces are generally better)
            face_area = (bottom - top) * (right - left)
            size_score = min(1.0, face_area / (100 * 100))  # Normalize to 100x100 baseline
            quality_score += size_score * 0.3
            
            # 2. Sharpness check using Laplacian variance
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 500)  # Normalize
            quality_score += sharpness_score * 0.4
            
            # 3. Brightness check
            mean_brightness = np.mean(gray_face)
            brightness_score = 1.0 - abs(mean_brightness - 128) / 128  # Optimal around 128
            quality_score += brightness_score * 0.3
            
            return min(1.0, quality_score)
            
        except Exception as e:
            print(f"Error assessing face quality: {e}")
            return 0.0
    
    def process_face_image(self, image_path: str) -> Optional[dict]:
        """
        Process an image to extract the best quality face and its encoding.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with face data or None if no suitable face found
        """
        faces_data = self.detect_faces(image_path)
        
        if not faces_data:
            return None
        
        best_face = None
        best_quality = 0.0
        
        # Find the best quality face
        for face_location, face_encoding in faces_data:
            quality = self.assess_face_quality(image_path, face_location)
            
            if quality > best_quality and quality >= self.quality_threshold:
                best_quality = quality
                best_face = {
                    'encoding': face_encoding.tolist(),  # Convert to list for JSON serialization
                    'location': face_location,
                    'quality': quality
                }
        
        return best_face
    
    def compare_faces(self, known_encoding: str, test_encoding: np.ndarray) -> Tuple[bool, float]:
        """
        Compare a known face encoding with a test encoding.
        
        Args:
            known_encoding: JSON string of known face encoding
            test_encoding: Test face encoding as numpy array
            
        Returns:
            Tuple of (is_match, confidence_score)
        """
        try:
            # Parse known encoding from JSON
            known_array = np.array(json.loads(known_encoding))
            
            # Calculate face distance
            face_distance = face_recognition.face_distance([known_array], test_encoding)[0]
            
            # Convert distance to confidence (0-1 scale)
            confidence = 1 - face_distance
            
            # Determine if it's a match
            is_match = face_distance <= self.max_face_distance
            
            return is_match, confidence
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, 0.0
    
    def verify_face_for_attendance(self, image_path: str, known_encodings: List[dict]) -> Optional[dict]:
        """
        Verify a face image against known encodings for attendance marking.
        
        Args:
            image_path: Path to the uploaded image
            known_encodings: List of dictionaries with user_id and encoding_data
            
        Returns:
            Dictionary with verification result or None if no match
        """
        # Process the uploaded image
        face_data = self.process_face_image(image_path)
        
        if not face_data:
            return {
                'success': False,
                'error': 'No clear face detected in the image',
                'quality_passed': False
            }
        
        test_encoding = np.array(face_data['encoding'])
        best_match = None
        best_confidence = 0.0
        
        # Compare against all known encodings
        for known_face in known_encodings:
            is_match, confidence = self.compare_faces(
                known_face['encoding_data'], 
                test_encoding
            )
            
            if is_match and confidence > best_confidence:
                best_confidence = confidence
                best_match = {
                    'user_id': known_face['user_id'],
                    'confidence': confidence,
                    'quality_score': face_data['quality']
                }
        
        if best_match:
            return {
                'success': True,
                'user_id': best_match['user_id'],
                'confidence': best_match['confidence'],
                'quality_score': best_match['quality_score'],
                'quality_passed': True
            }
        else:
            return {
                'success': False,
                'error': 'Face not recognized',
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