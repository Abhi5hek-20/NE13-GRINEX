#!/usr/bin/env python3
"""
Create a sample Excel file with valid image paths for testing
"""

import pandas as pd
import os

def create_sample_excel():
    """Create sample Excel file with valid image paths"""
    
    # Sample data with paths to the test images we just created
    test_images_folder = "C:/Users/abhis/Desktop/education/ai-attendance-system/test_images"
    
    data = [
        {
            'ROLL NO': '101',
            'NAME': 'ganesh',
            'PHOTO': os.path.join(test_images_folder, '101_ganesh.jpg')
        },
        {
            'ROLL NO': '102', 
            'NAME': 'saicharan',
            'PHOTO': os.path.join(test_images_folder, '102_saicharan.jpg')
        },
        {
            'ROLL NO': '103',
            'NAME': 'madhan', 
            'PHOTO': os.path.join(test_images_folder, '103_madhan.jpg')
        },
        {
            'ROLL NO': '104',
            'NAME': 'abhishek',
            'PHOTO': os.path.join(test_images_folder, '104_abhishek.jpg')
        },
        {
            'ROLL NO': '105',
            'NAME': 'anudeep',
            'PHOTO': os.path.join(test_images_folder, '105_anudeep.jpg')
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    excel_path = "C:/Users/abhis/Desktop/education/ai-attendance-system/dataset/test_students.xlsx"
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    
    df.to_excel(excel_path, index=False)
    print(f"Created sample Excel file: {excel_path}")
    
    # Show the data
    print("\nSample data:")
    print(df)
    
    return excel_path

if __name__ == "__main__":
    create_sample_excel()