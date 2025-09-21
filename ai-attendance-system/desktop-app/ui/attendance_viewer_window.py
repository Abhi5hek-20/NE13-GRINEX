"""
Individual attendance viewer window for AI Attendance System.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QComboBox, QTextEdit, QSplitter,
                            QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from services.face_recognition_service import FaceRecognitionService

class AttendanceViewerWindow(QWidget):
    """Window for viewing individual student attendance."""
    
    def __init__(self):
        super().__init__()
        self.face_service = FaceRecognitionService()
        self.init_ui()
        self.load_students()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Individual Attendance Viewer")
        self.setGeometry(100, 100, 1000, 700)
        
        main_layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("📊 Individual Attendance Tracker")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        main_layout.addWidget(header_label)
        
        # Student selection
        selection_layout = QHBoxLayout()
        
        selection_layout.addWidget(QLabel("Select Student:"))
        self.student_combo = QComboBox()
        self.student_combo.currentTextChanged.connect(self.on_student_changed)
        selection_layout.addWidget(self.student_combo)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_students)
        selection_layout.addWidget(refresh_btn)
        
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)
        
        # Splitter for summary and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Summary
        summary_group = QGroupBox("Student Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(200)
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        
        summary_group.setLayout(summary_layout)
        splitter.addWidget(summary_group)
        
        # Right side - Attendance history
        history_group = QGroupBox("Attendance History")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(['Date', 'Time', 'Status', 'Confidence', 'Class Info'])
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        splitter.addWidget(history_group)
        
        main_layout.addWidget(splitter)
        
        # All students summary button
        summary_btn = QPushButton("📈 View All Students Summary")
        summary_btn.clicked.connect(self.show_all_students_summary)
        main_layout.addWidget(summary_btn)
        
        self.setLayout(main_layout)
    
    def load_students(self):
        """Load students into the combo box."""
        try:
            db_info = self.face_service.get_database_info()
            students = db_info.get('students', [])
            
            self.student_combo.clear()
            self.student_combo.addItem("Select a student...")
            
            for student in students:
                display_text = f"{student['name']} ({student['roll_no']})"
                self.student_combo.addItem(display_text, student)
            
        except Exception as e:
            print(f"Error loading students: {e}")
    
    def on_student_changed(self):
        """Handle student selection change."""
        current_index = self.student_combo.currentIndex()
        if current_index > 0:  # Skip "Select a student..." option
            student_data = self.student_combo.itemData(current_index)
            if student_data:
                self.load_student_attendance(student_data)
    
    def load_student_attendance(self, student_data):
        """Load attendance data for selected student."""
        try:
            # Find the student ID from known faces
            student_id = None
            for sid, face_data in self.face_service.known_faces.items():
                if (face_data['name'] == student_data['name'] and 
                    face_data['roll_no'] == student_data['roll_no']):
                    student_id = sid
                    break
            
            if not student_id:
                self.summary_text.setText("Student not found in database.")
                self.history_table.setRowCount(0)
                return
            
            # Get attendance data
            attendance_data = self.face_service.get_individual_attendance(student_id)
            
            if not attendance_data:
                self.summary_text.setText("No attendance data found.")
                self.history_table.setRowCount(0)
                return
            
            # Update summary
            student_info = attendance_data['student_info']
            summary_text = f"""
            Student: {student_info['name']}
            Roll No: {student_info['roll_no']}
            Total Classes: {student_info['total_classes']}
            Classes Attended: {student_info['attended_classes']}
            Attendance Percentage: {student_info['attendance_percentage']:.1f}%
            
            Status: {'Good' if student_info['attendance_percentage'] >= 75 else 'Needs Improvement'}
            """
            self.summary_text.setPlainText(summary_text)
            
            # Update history table
            records = attendance_data['attendance_records']
            self.history_table.setRowCount(len(records))
            
            for i, record in enumerate(records):
                self.history_table.setItem(i, 0, QTableWidgetItem(record['date']))
                self.history_table.setItem(i, 1, QTableWidgetItem(record['time']))
                
                status_item = QTableWidgetItem(record['status'])
                if record['status'] == 'Present':
                    status_item.setBackground(Qt.green)
                else:
                    status_item.setBackground(Qt.red)
                self.history_table.setItem(i, 2, status_item)
                
                confidence = record.get('confidence', 0)
                self.history_table.setItem(i, 3, QTableWidgetItem(f"{confidence:.3f}"))
                
                class_info = f"{record.get('class_info', '')} - {record.get('section_info', '')}"
                self.history_table.setItem(i, 4, QTableWidgetItem(class_info))
            
            self.history_table.resizeRowsToContents()
            
        except Exception as e:
            print(f"Error loading student attendance: {e}")
            self.summary_text.setText(f"Error loading data: {e}")
    
    def show_all_students_summary(self):
        """Show summary for all students."""
        try:
            summary_data = self.face_service.get_all_students_attendance_summary()
            
            if not summary_data:
                self.summary_text.setText("No attendance data available.")
                return
            
            summary_text = "📊 ALL STUDENTS ATTENDANCE SUMMARY\n"
            summary_text += "=" * 50 + "\n\n"
            
            for student in summary_data:
                status = "✅ Good" if student['attendance_percentage'] >= 75 else "⚠️ Needs Improvement"
                summary_text += f"Name: {student['name']} ({student['roll_no']})\n"
                summary_text += f"Attendance: {student['attended_classes']}/{student['total_classes']} ({student['attendance_percentage']:.1f}%) {status}\n\n"
            
            self.summary_text.setPlainText(summary_text)
            self.history_table.setRowCount(0)
            
        except Exception as e:
            print(f"Error loading all students summary: {e}")
            self.summary_text.setText(f"Error loading data: {e}")