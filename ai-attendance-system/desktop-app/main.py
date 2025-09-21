#!/usr/bin/env python3
"""
AI Attendance System - PyQt5 Desktop Application
Main application entry point for teachers to upload group photos and mark attendance.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

# Load environment variables
load_dotenv()

class AttendanceApp(QMainWindow):
    """Main application class that manages the application flow."""
    
    def __init__(self):
        super().__init__()
        
        # Setup main window
        self.setWindowTitle("AI Attendance System")
        self.setMinimumSize(1200, 800)
        self.center_window()
        
        # Create main window directly (no login required)
        self.main_window = MainWindow()
        self.setCentralWidget(self.main_window)
        
    def center_window(self):
        """Center the window on the screen."""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AI Attendance System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AI Attendance Corp")
    
    # Create and show main window
    window = AttendanceApp()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()