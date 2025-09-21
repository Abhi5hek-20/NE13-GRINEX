# AI Attendance System

An intelligent attendance management system that uses face recognition technology to automatically mark student attendance from group photos or individual images.

## 🎯 Features

### Core Functionality
- **Face Recognition**: Advanced face detection and recognition using computer vision
- **Dataset Management**: Upload and manage student datasets via Excel files
- **Attendance Tracking**: Individual and group attendance marking with history
- **Real-time Processing**: Live photo processing with progress tracking
- **Individual Reports**: Detailed attendance statistics for each student

### User Interface
- **PyQt5 Desktop Application**: Professional, user-friendly interface
- **Drag & Drop Support**: Easy photo upload with drag-and-drop functionality
- **Progress Tracking**: Real-time progress updates during processing
- **Results Display**: Comprehensive attendance results with confidence scores

### Data Management
- **Excel Integration**: Import student data from Excel files with hyperlink support
- **SQLite Database**: Local attendance history storage
- **Image Processing**: Multi-format image support with validation
- **Statistics**: Attendance percentages and detailed reports

## 🏗️ Project Structure

```
ai-attendance-system/
├── backend/                    # FastAPI backend (optional)
│   ├── app/
│   │   ├── models/            # Database models
│   │   ├── routes/            # API endpoints
│   │   └── services/          # Business logic
│   └── requirements.txt       # Backend dependencies
│
├── desktop-app/               # Main PyQt5 Application
│   ├── main.py               # Application entry point
│   ├── ui/                   # User interface modules
│   │   ├── main_window.py    # Main application window
│   │   ├── dataset_upload_window.py  # Dataset upload interface
│   │   └── attendance_viewer.py      # Attendance history viewer
│   ├── services/             # Core services
│   │   ├── face_recognition_service.py  # Face recognition logic
│   │   └── attendance_tracker.py       # Attendance tracking
│   ├── utils/                # Utility modules
│   │   └── image_downloader.py        # Image processing utilities
│   └── requirements.txt      # Desktop app dependencies
│
├── dataset/                  # Student data storage
│   ├── student_details.xlsx  # Student information Excel file
│   ├── faces_db.json        # Face recognition database
│   └── attendance.db        # SQLite attendance database
│
└── README.md                # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Windows, macOS, or Linux

### Step 1: Clone the Repository
```bash
git clone https://github.com/Abhi5hek-20/NE13-GRINEX.git
cd ai-attendance-system
```

### Step 2: Install Dependencies
```bash
cd desktop-app
pip install -r requirements.txt
```

### Step 3: Install Additional Dependencies
```bash
pip install PyQt5 Pillow pandas openpyxl requests sqlite3
```

### Step 4: Run the Application
```bash
python main.py
```

## 📋 Dependencies

### Core Libraries
- **PyQt5**: Desktop GUI framework
- **Pillow (PIL)**: Image processing
- **pandas**: Excel file processing
- **openpyxl**: Excel hyperlink extraction
- **requests**: HTTP requests for image downloading
- **sqlite3**: Local database (built-in)

### Optional Backend Dependencies
- **FastAPI**: Web API framework
- **SQLAlchemy**: Database ORM
- **python-multipart**: File upload support

## 🎮 Usage Guide

### 1. Dataset Preparation

#### Excel File Format
Create an Excel file with the following columns:
- **ID**: Student ID/Roll Number
- **NAME**: Student full name
- **PHOTO**: Image file path, URL, or hyperlink

#### Example Excel Structure:
| ID | NAME | PHOTO |
|----|------|--------|
| 101 | John Doe | path/to/john.jpg |
| 102 | Jane Smith | https://example.com/jane.jpg |
| 103 | Bob Wilson | =HYPERLINK("path/to/bob.jpg","bob.jpg") |

### 2. Application Workflow

#### Step 1: Upload Dataset
1. Launch the application: `python main.py`
2. Click **"📚 Upload Dataset"**
3. Select your Excel file
4. Choose download folder for images
5. Wait for processing to complete

#### Step 2: Mark Attendance
1. Select **Class** and **Section** from dropdowns
2. Upload a group photo or individual photo:
   - **Drag & Drop**: Drag image file to the drop zone
   - **Browse**: Click "Browse" to select file
3. Click **"Process Attendance"**
4. View results in the table

#### Step 3: View Individual Attendance
1. After processing, click **"📊 View Attendance History"**
2. Browse individual student records
3. View attendance statistics and history

### 3. Features Overview

#### Face Recognition
- Detects faces in uploaded photos
- Compares with known student faces
- Returns confidence scores for matches
- Handles single and group photos

#### Attendance Tracking
- Marks attendance automatically
- Prevents duplicate entries for same day
- Calculates attendance percentages
- Maintains detailed history

#### Data Management
- Supports multiple image formats (JPG, PNG, BMP)
- Validates image files
- Handles various image sources (local files, URLs, hyperlinks)
- Creates local face recognition database

## 🔧 Configuration

### Settings Files
- **`.env`**: Environment variables
- **`requirements.txt`**: Python dependencies
- **`faces_db.json`**: Face recognition database
- **`attendance.db`**: SQLite attendance database

### Customization Options
- **Similarity Threshold**: Adjust face recognition sensitivity in `face_recognition_service.py`
- **UI Styling**: Modify colors and layouts in UI files
- **Database Path**: Change database location in service files

## 📊 Face Recognition Details

### Algorithm
- **Feature Extraction**: RGB analysis, brightness, contrast
- **Similarity Calculation**: Mathematical comparison of image features
- **Threshold Matching**: Configurable confidence threshold (default: 0.5)

### Image Requirements
- **Formats**: JPG, PNG, BMP, GIF
- **Size**: No specific limit (auto-resized to 100x100 for processing)
- **Quality**: Clear face visibility recommended

### Performance
- **Processing Speed**: ~1-2 seconds per image
- **Accuracy**: Depends on image quality and lighting
- **Database Size**: Supports hundreds of students

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Cannot identify image file" Error
**Problem**: Image files are HTML pages or corrupted
**Solution**: 
- Verify image files are actual images (not HTML pages)
- Use valid image formats (JPG, PNG, BMP)
- Check file integrity

#### 2. "No faces detected" Error
**Problem**: Face recognition cannot find faces
**Solution**:
- Ensure good lighting in photos
- Use clear, front-facing photos
- Check image quality and resolution

#### 3. Low Recognition Accuracy
**Problem**: Students not being recognized correctly
**Solution**:
- Use higher quality dataset images
- Ensure consistent lighting
- Adjust similarity threshold in settings

#### 4. Excel Import Issues
**Problem**: Dataset upload fails
**Solution**:
- Check Excel file format (columns: ID, NAME, PHOTO)
- Ensure image paths/URLs are valid
- Verify file permissions

### Debug Mode
Enable debug output by adding print statements in service files or check the console output for detailed error messages.

## 🎯 System Requirements

### Minimum Requirements
- **OS**: Windows 7/10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **RAM**: 4GB
- **Storage**: 500MB free space
- **Python**: 3.8+

### Recommended Requirements
- **RAM**: 8GB or more
- **Storage**: 2GB free space (for image datasets)
- **Camera**: For live photo capture (optional)

## 🔄 Updates & Maintenance

### Regular Maintenance
- **Database Cleanup**: Periodically archive old attendance records
- **Image Management**: Organize and backup student photos
- **Performance**: Monitor face recognition accuracy and adjust thresholds

### Feature Updates
- Enhanced face recognition algorithms
- Mobile app integration
- Cloud storage support
- Advanced reporting features

## 👥 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Add docstrings to functions and classes
- Include error handling and logging
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

### Getting Help
- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check this README and code comments
- **Email**: [Your contact email]

### FAQ

**Q: Can I use this for large classes?**
A: Yes, the system can handle hundreds of students. Performance depends on hardware.

**Q: Does it work with low-quality images?**
A: Face recognition accuracy decreases with poor image quality. Use clear, well-lit photos for best results.

**Q: Can I integrate this with existing systems?**
A: Yes, the system provides APIs and database export options for integration.

**Q: Is internet connection required?**
A: No, the desktop application works offline. Internet is only needed for downloading images from URLs.

## 🎉 Acknowledgments

- PyQt5 community for the excellent GUI framework
- Pillow developers for image processing capabilities
- pandas team for Excel integration support
- OpenCV community for computer vision resources

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Author**: Your Name  
**Repository**: https://github.com/Abhi5hek-20/NE13-GRINEX