"""
Image downloader utility for handling different image source types.
"""

import os
import requests
import urllib.parse
from pathlib import Path
from PIL import Image

class ImageDownloader:
    """Handles downloading images from various sources."""
    
    def __init__(self, download_folder):
        self.download_folder = Path(download_folder)
        self.download_folder.mkdir(exist_ok=True)
    
    def validate_and_fix_image(self, file_path):
        """Validate if file is actually an image and try to fix common issues."""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                print(f"Empty file: {file_path}")
                return None
            
            # Check if file is HTML disguised as image
            with open(file_path, 'rb') as f:
                header = f.read(50)
                if header.startswith(b'<!DOCTYPE') or header.startswith(b'<html'):
                    print(f"File is HTML, not an image: {file_path}")
                    return None
            
            # Try to open with PIL
            try:
                with Image.open(file_path) as img:
                    # File is valid, return the path
                    return file_path
            except Exception as e:
                print(f"Invalid image file {file_path}: {e}")
                return None
                
        except Exception as e:
            print(f"Error validating image {file_path}: {e}")
            return None
        
    def download_image(self, image_source, student_id, student_name):
        """
        Download image from various sources.
        
        Args:
            image_source: URL, file path, or filename
            student_id: Student ID for naming
            student_name: Student name for naming
            
        Returns:
            Path to downloaded/copied image file
        """
        try:
            # Clean student name for filename
            safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            # Case 1: Web URL (http/https)
            if str(image_source).startswith(('http://', 'https://')):
                return self._download_from_url(image_source, student_id, safe_name)
            
            # Case 2: Google Drive link
            elif 'drive.google.com' in str(image_source):
                return self._download_from_google_drive(image_source, student_id, safe_name)
            
            # Case 3: Dropbox link
            elif 'dropbox.com' in str(image_source):
                return self._download_from_dropbox(image_source, student_id, safe_name)
            
            # Case 4: Local file path
            elif os.path.exists(str(image_source)):
                return self._copy_local_file(image_source, student_id, safe_name)
            
            # Case 5: Filename only (assume it's in a specific folder)
            else:
                return self._find_and_copy_file(image_source, student_id, safe_name)
                
        except Exception as e:
            raise Exception(f"Failed to download image for {student_name}: {str(e)}")
    
    def _download_from_url(self, url, student_id, safe_name):
        """Download from direct URL."""
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get file extension from URL or content type
        ext = self._get_extension_from_url(url) or self._get_extension_from_content_type(response.headers.get('content-type'))
        
        filename = f"{student_id}_{safe_name}{ext}"
        file_path = self.download_folder / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(file_path)
    
    def _download_from_google_drive(self, drive_url, student_id, safe_name):
        """Download from Google Drive link."""
        # Extract file ID from Google Drive URL
        file_id = None
        if '/d/' in drive_url:
            file_id = drive_url.split('/d/')[1].split('/')[0]
        elif 'id=' in drive_url:
            file_id = drive_url.split('id=')[1].split('&')[0]
        
        if not file_id:
            raise Exception("Could not extract file ID from Google Drive URL")
        
        # Use direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return self._download_from_url(download_url, student_id, safe_name)
    
    def _download_from_dropbox(self, dropbox_url, student_id, safe_name):
        """Download from Dropbox link."""
        # Convert share URL to direct download URL
        if '?dl=0' in dropbox_url:
            download_url = dropbox_url.replace('?dl=0', '?dl=1')
        else:
            download_url = dropbox_url + ('&dl=1' if '?' in dropbox_url else '?dl=1')
        
        return self._download_from_url(download_url, student_id, safe_name)
    
    def _copy_local_file(self, file_path, student_id, safe_name):
        """Copy from local file system."""
        source_path = Path(file_path)
        ext = source_path.suffix
        filename = f"{student_id}_{safe_name}{ext}"
        dest_path = self.download_folder / filename
        
        import shutil
        shutil.copy2(source_path, dest_path)
        return str(dest_path)
    
    def _find_and_copy_file(self, filename, student_id, safe_name):
        """Find file in common locations and copy."""
        # Check if file exists in the dataset folder or its subfolders
        dataset_root = self.download_folder.parent
        possible_locations = [
            dataset_root,
            dataset_root / "images",
            dataset_root / "photos", 
            dataset_root / "student_photos",
            Path.cwd(),  # Current working directory
        ]
        
        for location in possible_locations:
            if location.exists():
                for file_path in location.rglob(str(filename)):
                    if file_path.is_file():
                        return self._copy_local_file(file_path, student_id, safe_name)
        
        # If not found, treat as original filename
        ext = Path(filename).suffix or '.jpg'
        new_filename = f"{student_id}_{safe_name}{ext}"
        dest_path = self.download_folder / new_filename
        
        # Create a placeholder or raise error
        raise Exception(f"Image file not found: {filename}")
    
    def _get_extension_from_url(self, url):
        """Extract file extension from URL."""
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        return Path(path).suffix or None
    
    def _get_extension_from_content_type(self, content_type):
        """Get file extension from content type."""
        if not content_type:
            return '.jpg'  # Default
        
        type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg', 
            'image/png': '.png',
            'image/bmp': '.bmp',
            'image/gif': '.gif',
            'image/tiff': '.tiff'
        }
        
        return type_map.get(content_type.lower(), '.jpg')