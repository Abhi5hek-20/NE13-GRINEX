# Dataset Organization

## 📁 Folder Structure:
```
ai-attendance-system/
└── dataset/
    ├── students.xlsx          ← Place your Excel file here
    └── student-images/        ← Place all student face images here
        ├── student1.jpg
        ├── student2.png
        ├── student3.jpeg
        └── ...
```

## 📋 Excel File Format:
Your Excel file should have exactly these column names:
- **id**: Student ID (e.g., STU001, STU002, etc.)
- **name**: Student full name (e.g., "John Doe")
- **image**: Image filename (e.g., "student1.jpg")

### Example Excel Content:
| id     | name          | image         |
|--------|---------------|---------------|
| STU001 | John Doe      | john_doe.jpg  |
| STU002 | Jane Smith    | jane.png      |
| STU003 | Mike Johnson  | mike.jpeg     |

## 📷 Image Requirements:
- **Formats**: JPG, PNG, JPEG, BMP
- **Content**: Clear face photos (one person per image)
- **Naming**: Must match exactly with the 'image' column in Excel
- **Size**: Any reasonable size (will be processed automatically)

## 🚀 How to Upload:
1. Place your Excel file in: `C:\Users\abhis\Desktop\education\ai-attendance-system\dataset\`
2. Place all student images in: `C:\Users\abhis\Desktop\education\ai-attendance-system\dataset\student-images\`
3. Open the PyQt5 application
4. Login as lecturer (lecturer@example.com / password123)
5. Click "📚 Upload Dataset" button
6. Select your Excel file and image folder
7. Click "🚀 Upload Dataset"

## ⚠️ Important Notes:
- Image filenames in Excel must match actual image files exactly
- Make sure all images contain clear, frontal face photos
- One student per image
- Good lighting and resolution preferred for better recognition