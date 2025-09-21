# Services package initialization
from .mock_face_recognition_service import MockFaceRecognitionService

# Use MockFaceRecognitionService for compatibility
FaceRecognitionService = MockFaceRecognitionService

__all__ = ["FaceRecognitionService", "MockFaceRecognitionService"]