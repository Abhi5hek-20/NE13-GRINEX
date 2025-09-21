#!/usr/bin/env python3
"""
Test script to create sample valid images for testing face recognition
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

def create_sample_images():
    """Create sample face images for testing"""
    # Create test images folder
    test_folder = "C:/Users/abhis/Desktop/education/ai-attendance-system/test_images"
    os.makedirs(test_folder, exist_ok=True)
    
    # Sample student data
    students = [
        {"id": "101", "name": "ganesh"},
        {"id": "102", "name": "saicharan"},
        {"id": "103", "name": "madhan"},
        {"id": "104", "name": "abhishek"},
        {"id": "105", "name": "anudeep"}
    ]
    
    # Create simple test images
    for student in students:
        # Create a simple colored rectangle as a "face"
        img = Image.new('RGB', (200, 200), color=(
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        ))
        
        # Add some "face-like" features (circles for eyes, etc.)
        draw = ImageDraw.Draw(img)
        
        # Draw eyes
        draw.ellipse([50, 60, 70, 80], fill='black')
        draw.ellipse([130, 60, 150, 80], fill='black')
        
        # Draw nose
        draw.ellipse([95, 90, 105, 110], fill='brown')
        
        # Draw mouth
        draw.ellipse([80, 130, 120, 150], fill='red')
        
        # Add student name
        try:
            font = ImageFont.load_default()
            draw.text((10, 10), student['name'], fill='white', font=font)
        except:
            draw.text((10, 10), student['name'], fill='white')
        
        # Save image
        filename = f"{student['id']}_{student['name']}.jpg"
        filepath = os.path.join(test_folder, filename)
        img.save(filepath, 'JPEG')
        print(f"Created: {filepath}")
    
    print(f"\nCreated {len(students)} test images in {test_folder}")
    return test_folder

if __name__ == "__main__":
    create_sample_images()