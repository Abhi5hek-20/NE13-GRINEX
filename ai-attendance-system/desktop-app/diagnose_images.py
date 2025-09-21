#!/usr/bin/env python3
"""
Image diagnostic script to check what's wrong with the image files
"""

import os
from PIL import Image

def diagnose_image_file(image_path):
    """Diagnose issues with an image file."""
    print(f"\n=== Diagnosing: {image_path} ===")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print("❌ File does not exist")
        return False
    
    # Check file size
    file_size = os.path.getsize(image_path)
    print(f"📁 File size: {file_size} bytes")
    
    if file_size == 0:
        print("❌ File is empty (0 bytes)")
        return False
    
    # Check file type using python-magic (if available)
    try:
        import magic
        file_type = magic.from_file(image_path, mime=True)
        print(f"🔍 Detected MIME type: {file_type}")
    except ImportError:
        print("⚠️ python-magic not available, skipping MIME detection")
    except Exception as e:
        print(f"⚠️ Error detecting file type: {e}")
    
    # Try to read file header
    try:
        with open(image_path, 'rb') as f:
            header = f.read(16)
            print(f"📄 File header (hex): {header.hex()}")
            print(f"📄 File header (ascii): {header}")
    except Exception as e:
        print(f"❌ Error reading file header: {e}")
        return False
    
    # Try PIL
    try:
        with Image.open(image_path) as img:
            print(f"✅ PIL can open image")
            print(f"📸 Format: {img.format}")
            print(f"📏 Size: {img.size}")
            print(f"🎨 Mode: {img.mode}")
            return True
    except Exception as e:
        print(f"❌ PIL error: {e}")
        return False

def test_sample_images():
    """Test a few sample images from the error log."""
    test_images = [
        r"C:\Users\abhis\Desktop\varunreport\4068_ganesh.jpg",
        r"C:\Users\abhis\Desktop\varunreport\6608_saicharan.jpg",
        r"C:\Users\abhis\Desktop\varunreport\6690_abhishek.jpg"
    ]
    
    working_count = 0
    
    for img_path in test_images:
        if diagnose_image_file(img_path):
            working_count += 1
    
    print(f"\n=== Summary ===")
    print(f"✅ Working images: {working_count}/{len(test_images)}")
    print(f"❌ Broken images: {len(test_images) - working_count}/{len(test_images)}")

if __name__ == "__main__":
    test_sample_images()