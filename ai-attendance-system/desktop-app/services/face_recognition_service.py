"""
Face recognition service for the AI Attendance System.
Simple implementation using basic image comparison.
"""

import os
import json
from PIL import Image, ImageStat
import hashlib
from .attendance_tracker import AttendanceTracker

class FaceRecognitionService:
    """Service for face detection and recognition using basic image comparison."""
    
    def __init__(self, dataset_folder="dataset"):
        self.dataset_folder = dataset_folder
        self.known_faces = {}
        self.attendance_tracker = AttendanceTracker()
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known faces from the dataset folder."""
        try:
            # Look for a faces database file
            db_path = os.path.join(self.dataset_folder, 'faces_db.json')
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    faces_data = json.load(f)
                    for student_id, data in faces_data.items():
                        self.known_faces[student_id] = {
                            'name': data['name'],
                            'roll_no': data['roll_no'],
                            'image_path': data['image_path'],
                            'features': data.get('features', None)
                        }
                print(f"Loaded {len(self.known_faces)} known faces from database")
        except Exception as e:
            print(f"Error loading known faces: {e}")
            self.known_faces = {}
    
    def extract_simple_features(self, image_path):
        """Extract simple features from an image."""
        try:
            # First check if the file is actually an image
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return None
            
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                print(f"Empty file: {image_path}")
                return None
            
            # Check if file is actually HTML (common issue)
            with open(image_path, 'rb') as f:
                header = f.read(20)
                if header.startswith(b'<!DOCTYPE') or header.startswith(b'<html'):
                    print(f"File is HTML, not an image: {image_path}")
                    return None
                if not (header.startswith(b'\xff\xd8\xff') or  # JPEG
                       header.startswith(b'\x89PNG') or        # PNG
                       header.startswith(b'BM')):              # BMP
                    print(f"File doesn't have valid image header: {image_path}")
                    return None
            
            # Open image with PIL
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to standard size
            image = image.resize((100, 100))
            
            # Calculate basic statistics
            stat = ImageStat.Stat(image)
            
            # Get mean values for R, G, B channels
            mean_rgb = stat.mean
            
            # Get extrema (min, max) for each channel
            extrema = stat.extrema
            
            # Create simple feature vector
            features = {
                'mean_r': mean_rgb[0],
                'mean_g': mean_rgb[1],
                'mean_b': mean_rgb[2],
                'brightness': sum(mean_rgb) / 3,
                'contrast': sum([(ext[1] - ext[0]) for ext in extrema]) / 3
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting features from {image_path}: {e}")
            return None
    
    def build_faces_database(self, student_data_list):
        """Build faces database from uploaded student data."""
        faces_db = {}
        processed_count = 0
        
        for student in student_data_list:
            try:
                student_id = str(student.get('student_id', ''))
                name = student.get('name', '')
                roll_no = student.get('roll_no', student_id)
                image_path = student.get('image_path', '')
                
                if not os.path.exists(image_path):
                    print(f"Image not found for {name}: {image_path}")
                    continue
                
                # Validate image file
                from utils.image_downloader import ImageDownloader
                validator = ImageDownloader("temp")
                valid_image_path = validator.validate_and_fix_image(image_path)
                
                if not valid_image_path:
                    print(f"Invalid image file for {name}: {image_path}")
                    continue
                
                # Extract simple features
                features = self.extract_simple_features(valid_image_path)
                
                if features is not None:
                    faces_db[student_id] = {
                        'name': name,
                        'roll_no': roll_no,
                        'image_path': image_path,
                        'features': features
                    }
                    processed_count += 1
                    print(f"Processed face for {name}")
                else:
                    print(f"Could not process image for {name}")
                    
            except Exception as e:
                print(f"Error processing {student.get('name', 'Unknown')}: {e}")
        
        # Save to database file
        try:
            db_path = os.path.join(self.dataset_folder, 'faces_db.json')
            os.makedirs(self.dataset_folder, exist_ok=True)
            
            with open(db_path, 'w') as f:
                json.dump(faces_db, f, indent=2)
            
            print(f"Saved {processed_count} faces to database")
            
            # Reload the known faces
            self.load_known_faces()
            
            return {
                'processed_count': processed_count,
                'total_students': len(student_data_list),
                'database_path': db_path
            }
            
        except Exception as e:
            print(f"Error saving faces database: {e}")
            return {'processed_count': 0, 'total_students': len(student_data_list)}
    
    def simple_image_similarity(self, features1, features2):
        """Calculate simple similarity between two feature sets."""
        if not features1 or not features2:
            return 0.0
        
        try:
            # Calculate differences in key features
            brightness_diff = abs(features1['brightness'] - features2['brightness']) / 255.0
            contrast_diff = abs(features1['contrast'] - features2['contrast']) / 255.0
            
            # Calculate RGB differences
            r_diff = abs(features1['mean_r'] - features2['mean_r']) / 255.0
            g_diff = abs(features1['mean_g'] - features2['mean_g']) / 255.0
            b_diff = abs(features1['mean_b'] - features2['mean_b']) / 255.0
            
            # Calculate overall similarity (1.0 = identical, 0.0 = completely different)
            total_diff = (brightness_diff + contrast_diff + r_diff + g_diff + b_diff) / 5.0
            similarity = 1.0 - total_diff
            
            return max(0.0, similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def detect_and_recognize_faces(self, image_path, class_info='', section_info=''):
        """Detect and recognize faces in a group photo."""
        try:
            # For simplicity, assume the uploaded image contains one face
            # In a real implementation, you would use face detection here
            
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Uploaded image file not found',
                    'detected_faces': 0,
                    'recognized_students': 0,
                    'attendance_list': []
                }
            
            # Check if uploaded file is actually an image
            with open(image_path, 'rb') as f:
                header = f.read(20)
                if header.startswith(b'<!DOCTYPE') or header.startswith(b'<html'):
                    return {
                        'success': False,
                        'error': 'Uploaded file is HTML, not an image. Please upload a valid image file.',
                        'detected_faces': 0,
                        'recognized_students': 0,
                        'attendance_list': []
                    }
            
            # Extract features from the uploaded image
            uploaded_features = self.extract_simple_features(image_path)
            
            if uploaded_features is None:
                return {
                    'success': False,
                    'error': 'Could not process the uploaded image. Please ensure it\'s a valid image file.',
                    'detected_faces': 0,
                    'recognized_students': 0,
                    'attendance_list': []
                }
            
            print(f"Processing uploaded image with {len(self.known_faces)} known faces in database")
            
            if len(self.known_faces) == 0:
                return {
                    'success': False,
                    'error': 'No student faces in database. Please upload a dataset first.',
                    'detected_faces': 1,
                    'recognized_students': 0,
                    'attendance_list': []
                }
            
            # Assume 1 face detected (the uploaded image itself)
            detected_faces = 1
            attendance_list = []
            recognized_count = 0
            
            # Compare with known faces
            best_match = None
            best_similarity = 0.0
            similarity_threshold = 0.5  # Lowered threshold for more lenient matching
            
            for student_id, known_face in self.known_faces.items():
                if known_face['features']:
                    similarity = self.simple_image_similarity(uploaded_features, known_face['features'])
                    print(f"Similarity with {known_face['name']}: {similarity:.3f}")
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = known_face
                        best_match['student_id'] = student_id
            
            if best_match and best_similarity > similarity_threshold:
                # Mark attendance in database
                self.attendance_tracker.mark_attendance(
                    student_id=best_match['student_id'],
                    student_name=best_match['name'],
                    roll_no=best_match['roll_no'],
                    status='Present',
                    confidence=best_similarity,
                    class_info=class_info,
                    section_info=section_info,
                    image_path=image_path
                )
                
                # Get individual attendance data
                individual_data = self.attendance_tracker.get_student_attendance(best_match['student_id'])
                
                attendance_list.append({
                    'name': best_match['name'],
                    'roll_no': best_match['roll_no'],
                    'status': 'Present',
                    'confidence': f"{best_similarity:.3f}",
                    'face_position': "Detected Face",
                    'individual_stats': individual_data['student_info'] if individual_data else None
                })
                recognized_count = 1
                print(f"Recognized: {best_match['name']} (confidence: {best_similarity:.3f})")
            else:
                attendance_list.append({
                    'name': 'Unknown Person',
                    'roll_no': 'N/A',
                    'status': 'Unknown',
                    'confidence': f"{best_similarity:.3f}" if best_similarity > 0 else "0.000",
                    'face_position': "Detected Face",
                    'individual_stats': None
                })
                print(f"Unknown face (best similarity: {best_similarity:.3f})")
            
            return {
                'success': True,
                'detected_faces': detected_faces,
                'recognized_students': recognized_count,
                'attendance_list': attendance_list,
                'message': f'Detected {detected_faces} face, recognized {recognized_count} student(s)',
                'best_similarity': best_similarity,
                'threshold_used': similarity_threshold
            }
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return {
                'success': False,
                'error': str(e),
                'detected_faces': 0,
                'recognized_students': 0,
                'attendance_list': []
            }
    
    def get_database_info(self):
        """Get information about the current faces database."""
        return {
            'known_faces_count': len(self.known_faces),
            'database_path': os.path.join(self.dataset_folder, 'faces_db.json'),
            'students': [
                {
                    'name': face['name'],
                    'roll_no': face['roll_no'],
                    'has_features': face['features'] is not None
                }
                for face in self.known_faces.values()
            ]
        }
    
    def get_individual_attendance(self, student_id):
        """Get individual attendance data for a student."""
        return self.attendance_tracker.get_student_attendance(student_id)
    
    def get_all_students_attendance_summary(self):
        """Get attendance summary for all students."""
        return self.attendance_tracker.get_all_students_summary()