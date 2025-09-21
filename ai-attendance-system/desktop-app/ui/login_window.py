"""
Login window for teacher authentication.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame,
                            QProgressBar, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QPalette

class LoginWorker(QThread):
    """Worker thread for login authentication to prevent UI freezing."""
    
    login_result = pyqtSignal(bool, object, str)  # success, user_data, error_message
    
    def __init__(self, auth_service, email, password):
        super().__init__()
        self.auth_service = auth_service
        self.email = email
        self.password = password
    
    def run(self):
        """Perform login in background thread."""
        try:
            user_data = self.auth_service.login(self.email, self.password)
            self.login_result.emit(True, user_data, "")
        except Exception as e:
            self.login_result.emit(False, None, str(e))

class LoginWindow(QWidget):
    """Login window widget for teacher authentication."""
    
    login_successful = pyqtSignal(object)  # Emits user data
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.login_worker = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("AI Attendance System")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        subtitle_label = QLabel("Teacher Login")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Login form
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Box)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Email field
        email_label = QLabel("Email:")
        email_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ecf0f1;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        # Sample credentials section
        sample_frame = QFrame()
        sample_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        sample_layout = QVBoxLayout(sample_frame)
        
        sample_title = QLabel("Sample Credentials for Testing:")
        sample_title.setStyleSheet("font-weight: bold; color: #495057;")
        
        lecturer_btn = QPushButton("Use Lecturer Account")
        lecturer_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        lecturer_btn.clicked.connect(self.fill_lecturer_credentials)
        
        sample_layout.addWidget(sample_title)
        sample_layout.addWidget(lecturer_btn)
        
        # Add widgets to form layout
        form_layout.addWidget(email_label, 0, 0)
        form_layout.addWidget(self.email_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        form_layout.addWidget(self.login_button, 2, 0, 1, 2)
        form_layout.addWidget(self.progress_bar, 3, 0, 1, 2)
        
        # Add everything to main layout
        layout.addLayout(title_layout)
        layout.addWidget(form_frame)
        layout.addWidget(sample_frame)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Connect signals
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Set initial focus
        self.email_input.setFocus()
        
    def fill_lecturer_credentials(self):
        """Fill in sample lecturer credentials."""
        self.email_input.setText("lecturer@example.com")
        self.password_input.setText("password123")
        
    def handle_login(self):
        """Handle login button click."""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return
        
        # Disable UI during login
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start login worker thread
        self.login_worker = LoginWorker(self.auth_service, email, password)
        self.login_worker.login_result.connect(self.on_login_result)
        self.login_worker.start()
    
    @pyqtSlot(bool, object, str)
    def on_login_result(self, success, user_data, error_message):
        """Handle login result from worker thread."""
        # Re-enable UI
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            # Check if user is a lecturer
            if user_data and user_data.get('role') == 'lecturer':
                self.login_successful.emit(user_data)
            else:
                QMessageBox.warning(
                    self, 
                    "Access Denied", 
                    "This application is only for lecturers/teachers."
                )
        else:
            QMessageBox.critical(
                self, 
                "Login Failed", 
                f"Login failed: {error_message}"
            )
        
        # Clean up worker
        if self.login_worker:
            self.login_worker.deleteLater()
            self.login_worker = None
    
    def set_ui_enabled(self, enabled):
        """Enable or disable UI elements."""
        self.email_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.login_button.setEnabled(enabled)
    
    def clear_form(self):
        """Clear login form."""
        self.email_input.clear()
        self.password_input.clear()
        self.email_input.setFocus()