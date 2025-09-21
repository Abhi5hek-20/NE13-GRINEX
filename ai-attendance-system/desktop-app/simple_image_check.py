#!/usr/bin/env python3
"""
Simple image diagnostic script
"""

import os
from PIL import Image

def check_images():
    """Check image files in the varunreport folder"""
    folder = "C:/Users/abhis/Desktop/varunreport"
    
    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        return
    
    print(f"Checking images in: {folder}")
    print("=" * 50)
    
    # Get all JPG files
    jpg_files = [f for f in os.listdir(folder) if f.lower().endswith('.jpg')]
    print(f"Found {len(jpg_files)} JPG files")
    
    working = 0
    broken = 0
    
    for filename in jpg_files[:5]:  # Check first 5
        filepath = os.path.join(folder, filename)
        print(f"\nChecking: {filename}")
        
        # Check file size
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  Size: {size} bytes")
            
            if size == 0:
                print("  ❌ Empty file")
                broken += 1
                continue
        
        # Try to open with PIL
        try:
            with Image.open(filepath) as img:
                print(f"  ✅ PIL Success: {img.format} {img.size} {img.mode}")
                working += 1
        except Exception as e:
            print(f"  ❌ PIL Error: {e}")
            broken += 1
            
            # Check file header
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(10)
                    print(f"  Header: {header.hex()}")
            except:
                print("  Cannot read file header")
    
    print(f"\nSummary: {working} working, {broken} broken")

if __name__ == "__main__":
    check_images()