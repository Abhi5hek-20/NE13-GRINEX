"""
Main window for group photo upload and attendance marking.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QTextEdit, QFileDialog,
                            QMessageBox, QFrame, QProgressBar, QScrollArea,
                            QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QMimeData
from PyQt5.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent
from ui.dataset_upload_window import DatasetUploadWindow
from ui.attendance_viewer_window import AttendanceViewerWindow
from services.face_recognition_service import FaceRecognitionService

class PhotoUploadWorker(QThread):
    """Worker thread for photo upload and processing."""
    
    upload_result = pyqtSignal(bool, object, str)  # success, result_data, error_message
    progress_update = pyqtSignal(int)  # progress percentage
    
    def __init__(self, class_id, section_id, image_path, class_data=None, section_data=None):
        super().__init__()
        self.class_id = class_id
        self.section_id = section_id
        self.image_path = image_path
        self.class_data = class_data
        self.section_data = section_data
    
    def run(self):
        """Process photo and perform real face recognition."""
        try:
            self.progress_update.emit(20)
            
            # Initialize face recognition service
            face_service = FaceRecognitionService()
            
            self.progress_update.emit(40)
            
            # Perform face detection and recognition
            class_info = f"{self.class_data['name']} - {self.class_data['subject']}" if self.class_data else ''
            section_info = self.section_data['name'] if self.section_data else ''
            
            result = face_service.detect_and_recognize_faces(
                self.image_path, 
                class_info=class_info, 
                section_info=section_info
            )
            
            self.progress_update.emit(80)
            
            if result['success']:
                # Format the result to match expected structure
                formatted_result = {
                    'detected_faces': result['detected_faces'],
                    'recognized_students': result['recognized_students'],
                    'attendance_marked': result['recognized_students'],
                    'attendance_list': result['attendance_list'],
                    'message': result.get('message', 'Processing completed')
                }
                
                self.progress_update.emit(100)
                self.upload_result.emit(True, formatted_result, "")
            else:
                error_msg = result.get('error', 'Face recognition failed')
                self.upload_result.emit(False, None, error_msg)
                
        except Exception as e:
            error_msg = f"Error during face recognition: {str(e)}"
            print(error_msg)
            self.upload_result.emit(False, None, error_msg)

class PhotoDropZone(QLabel):
    """Drag and drop zone for photo upload."""
    
    photo_dropped = pyqtSignal(str)  # file path
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 16px;
                padding: 20px;
            }
            QLabel:hover {
                background-color: #e9ecef;
                border-color: #2980b9;
            }
        """)
        self.setText("📷 Drag and drop group photo here\nor click 'Browse' to select a file\n\n"
                    "Supported formats: JPG, PNG, JPEG")
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self.is_image_file(urls[0].toLocalFile()):
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QLabel {
                        border: 3px dashed #28a745;
                        border-radius: 10px;
                        background-color: #d4edda;
                        color: #155724;
                        font-size: 16px;
                        padding: 20px;
                    }
                """)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 16px;
                padding: 20px;
            }
            QLabel:hover {
                background-color: #e9ecef;
                border-color: #2980b9;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if self.is_image_file(file_path):
                self.photo_dropped.emit(file_path)
                event.acceptProposedAction()
        
        # Reset styling
        self.dragLeaveEvent(event)
    
    def is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format."""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        return any(file_path.lower().endswith(ext) for ext in valid_extensions)

class MainWindow(QWidget):
    """Main application window for photo upload and attendance management."""
    
    def __init__(self):
        super().__init__()
        self.upload_worker = None
        self.classes = []
        self.sections = []
        self.selected_image_path = None
        self.attendance_results = []
        
        self.init_ui()
        self.load_classes()
        
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_layout = QHBoxLayout()
        
        title_label = QLabel("AI Attendance System - Teacher Dashboard")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50;")
        
        # Dataset upload button
        dataset_btn = QPushButton("📚 Upload Dataset")
        dataset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a2d91;
            }
        """)
        dataset_btn.clicked.connect(self.open_dataset_upload)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(dataset_btn)
        
        # Main content using splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Photo upload and class selection
        left_panel = QFrame()
        left_panel.setMaximumWidth(400)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        left_layout = QVBoxLayout(left_panel)
        
        # Class and Section selection
        selection_group = QGroupBox("1. Select Class and Section")
        selection_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        selection_layout = QVBoxLayout(selection_group)
        
        # Class selection
        class_label = QLabel("Class:")
        class_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.class_combo = QComboBox()
        self.class_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.class_combo.currentTextChanged.connect(self.on_class_changed)
        
        # Section selection
        section_label = QLabel("Section:")
        section_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.section_combo = QComboBox()
        self.section_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ecf0f1;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        
        selection_layout.addWidget(class_label)
        selection_layout.addWidget(self.class_combo)
        selection_layout.addWidget(section_label)
        selection_layout.addWidget(self.section_combo)
        
        # Photo upload section
        upload_group = QGroupBox("2. Upload Group Photo")
        upload_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        upload_layout = QVBoxLayout(upload_group)
        
        # Drop zone
        self.drop_zone = PhotoDropZone()
        self.drop_zone.photo_dropped.connect(self.on_photo_selected)
        
        # Browse button
        browse_btn = QPushButton("📁 Browse Files")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        browse_btn.clicked.connect(self.browse_photo)
        
        upload_layout.addWidget(self.drop_zone)
        upload_layout.addWidget(browse_btn)
        
        # Process button
        self.process_btn = QPushButton("🎯 Process Attendance")
        self.process_btn.setEnabled(False)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.process_btn.clicked.connect(self.process_attendance)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)
        
        # Selected image info
        self.image_info_label = QLabel("No image selected")
        self.image_info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        
        left_layout.addWidget(selection_group)
        left_layout.addWidget(upload_group)
        left_layout.addWidget(self.image_info_label)
        left_layout.addWidget(self.process_btn)
        left_layout.addWidget(self.progress_bar)
        left_layout.addStretch()
        
        # Right panel - Results display
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        right_layout = QVBoxLayout(right_panel)
        
        # Results header with button
        results_header_layout = QHBoxLayout()
        
        results_label = QLabel("Attendance Results")
        results_font = QFont()
        results_font.setPointSize(16)
        results_font.setBold(True)
        results_label.setFont(results_font)
        results_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        results_header_layout.addWidget(results_label)
        
        results_header_layout.addStretch()
        
        view_attendance_btn = QPushButton("👤 View Individual Attendance")
        view_attendance_btn.clicked.connect(self.open_attendance_viewer)
        view_attendance_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        results_header_layout.addWidget(view_attendance_btn)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(['Photo', 'Student Name', 'Status', 'Confidence', 'Attendance Info'])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.setColumnWidth(0, 80)
        
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 10px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        # Status summary
        self.status_label = QLabel("Ready to process attendance")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #d1ecf1;
                color: #0c5460;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #bee5eb;
            }
        """)
        
        right_layout.addLayout(results_header_layout)
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.results_table)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        # Add everything to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
        
    def load_classes(self):
        """Load sample classes for demo purposes."""
        try:
            # Sample classes for demo
            self.classes = [
                {'id': 1, 'name': 'Class 10A', 'subject': 'Mathematics'},
                {'id': 2, 'name': 'Class 10B', 'subject': 'Physics'},
                {'id': 3, 'name': 'Class 11A', 'subject': 'Chemistry'},
                {'id': 4, 'name': 'Class 12A', 'subject': 'Computer Science'}
            ]
            
            self.class_combo.clear()
            self.class_combo.addItem("Select a class...")
            
            for class_item in self.classes:
                display_text = f"{class_item['name']} - {class_item['subject']}"
                self.class_combo.addItem(display_text, class_item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load classes: {str(e)}")
    
    def on_class_changed(self):
        """Handle class selection change."""
        current_index = self.class_combo.currentIndex()
        if current_index > 0:  # Skip "Select a class..." option
            class_data = self.class_combo.itemData(current_index)
            if class_data:
                self.load_sections(class_data['id'])
        else:
            self.section_combo.clear()
            self.section_combo.addItem("Select a section...")
    
    def load_sections(self, class_id):
        """Load sample sections for selected class."""
        try:
            # Sample sections for demo
            self.sections = [
                {'id': 1, 'name': 'Section A'},
                {'id': 2, 'name': 'Section B'},
                {'id': 3, 'name': 'Section C'}
            ]
            
            self.section_combo.clear()
            self.section_combo.addItem("Select a section...")
            
            for section in self.sections:
                self.section_combo.addItem(section['name'], section)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load sections: {str(e)}")
    
    def browse_photo(self):
        """Open file dialog to select photo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Group Photo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self.on_photo_selected(file_path)
    
    def on_photo_selected(self, file_path):
        """Handle photo selection."""
        self.selected_image_path = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        self.image_info_label.setText(f"📷 {file_name} ({file_size:.1f} MB)")
        self.image_info_label.setStyleSheet("color: #28a745; font-weight: bold;")
        
        # Update drop zone
        self.drop_zone.setText(f"✅ Photo selected: {file_name}\n\nClick 'Browse' to select a different photo")
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 3px solid #28a745;
                border-radius: 10px;
                background-color: #d4edda;
                color: #155724;
                font-size: 14px;
                padding: 20px;
            }
        """)
        
        self.check_ready_to_process()
    
    def check_ready_to_process(self):
        """Check if ready to process attendance."""
        has_image = self.selected_image_path is not None
        has_class = self.class_combo.currentIndex() > 0
        has_section = self.section_combo.currentIndex() > 0
        
        self.process_btn.setEnabled(has_image and has_class and has_section)
    
    def process_attendance(self):
        """Process attendance from uploaded photo."""
        if not self.selected_image_path:
            QMessageBox.warning(self, "Error", "Please select a photo first.")
            return
        
        class_data = self.class_combo.itemData(self.class_combo.currentIndex())
        section_data = self.section_combo.itemData(self.section_combo.currentIndex())
        
        if not class_data or not section_data:
            QMessageBox.warning(self, "Error", "Please select both class and section.")
            return
        
        # Disable UI during processing
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        self.status_label.setText("🔄 Processing photo and identifying students...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                color: #856404;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ffeaa7;
            }
        """)
        
        # Start processing worker
        self.upload_worker = PhotoUploadWorker(
            class_data['id'],
            section_data['id'],
            self.selected_image_path,
            class_data,
            section_data
        )
        self.upload_worker.upload_result.connect(self.on_upload_result)
        self.upload_worker.progress_update.connect(self.progress_bar.setValue)
        self.upload_worker.start()
    
    @pyqtSlot(bool, object, str)
    def on_upload_result(self, success, result_data, error_message):
        """Handle upload and processing result."""
        # Re-enable UI
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.display_results(result_data)
        else:
            self.status_label.setText(f"❌ Error: {error_message}")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 10px;
                    border-radius: 4px;
                    border: 1px solid #f5c6cb;
                }
            """)
            QMessageBox.critical(self, "Processing Error", f"Failed to process attendance: {error_message}")
        
        # Clean up worker
        if self.upload_worker:
            self.upload_worker.deleteLater()
            self.upload_worker = None
    
    def display_results(self, result_data):
        """Display attendance processing results."""
        self.attendance_results = result_data.get('attendance_records', [])
        recognized_count = result_data.get('recognized_students', 0)
        total_faces = result_data.get('total_faces_detected', 0)
        
        # Update status
        self.status_label.setText(
            f"✅ Processing complete! Recognized {recognized_count} students out of {total_faces} faces detected."
        )
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #d4edda;
                color: #155724;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #c3e6cb;
            }
        """)
        
        # Populate results table
        self.results_table.setRowCount(len(self.attendance_results))
        
        for i, record in enumerate(self.attendance_results):
            # Student photo (if available)
            photo_label = QLabel()
            if record.get('student_photo'):
                # This would load the student's registered photo
                photo_label.setText("📷")
            else:
                photo_label.setText("❓")
            photo_label.setAlignment(Qt.AlignCenter)
            self.results_table.setCellWidget(i, 0, photo_label)
            
            # Student name
            name_item = QTableWidgetItem(record.get('student_name', 'Unknown'))
            self.results_table.setItem(i, 1, name_item)
            
            # Status
            status = record.get('status', 'absent')
            status_item = QTableWidgetItem(status.title())
            if status == 'present':
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.red)
            self.results_table.setItem(i, 2, status_item)
            
            # Confidence
            confidence = record.get('confidence', 0)
            confidence_item = QTableWidgetItem(f"{confidence:.1%}")
            self.results_table.setItem(i, 3, confidence_item)
            
            # Individual attendance info
            individual_stats = record.get('individual_stats')
            if individual_stats:
                attendance_info = (
                    f"Classes: {individual_stats['attended_classes']}/{individual_stats['total_classes']}\n"
                    f"Percentage: {individual_stats['attendance_percentage']:.1f}%"
                )
            else:
                attendance_info = "No data available"
            
            attendance_item = QTableWidgetItem(attendance_info)
            self.results_table.setItem(i, 4, attendance_item)
        
        self.results_table.resizeRowsToContents()
    
    def set_ui_enabled(self, enabled):
        """Enable or disable UI elements."""
        self.class_combo.setEnabled(enabled)
        self.section_combo.setEnabled(enabled)
        self.process_btn.setEnabled(enabled and self.selected_image_path is not None)
        
        # Update process button connection
        if enabled:
            self.class_combo.currentTextChanged.connect(self.on_class_changed)
            self.section_combo.currentTextChanged.connect(self.check_ready_to_process)
        else:
            self.class_combo.currentTextChanged.disconnect()
            try:
                self.section_combo.currentTextChanged.disconnect()
            except:
                pass
    
    def open_dataset_upload(self):
        """Open dataset upload window."""
        dataset_window = DatasetUploadWindow()
        dataset_window.upload_completed.connect(self.on_dataset_uploaded)
        dataset_window.show()
        
        # Keep reference to prevent garbage collection
        self.dataset_window = dataset_window
    
    def on_dataset_uploaded(self, result_data):
        """Handle dataset upload completion."""
        processed_count = result_data.get('processed', 0)
        face_db_count = result_data.get('face_db_processed', 0)
        QMessageBox.information(
            self,
            "Dataset Uploaded",
            f"Successfully uploaded {processed_count} student records.\n"
            f"Face recognition database: {face_db_count} faces processed.\n"
            "You can now process group photos for attendance marking."
        )
    
    def open_attendance_viewer(self):
        """Open individual attendance viewer window."""
        try:
            self.attendance_viewer = AttendanceViewerWindow()
            self.attendance_viewer.show()
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not open attendance viewer: {str(e)}"
            )