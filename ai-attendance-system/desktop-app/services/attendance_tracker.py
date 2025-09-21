"""
Individual attendance tracking service for AI Attendance System.
Tracks attendance history for each student individually.
"""

import os
import json
from datetime import datetime, timedelta
import sqlite3

class AttendanceTracker:
    """Service for tracking individual student attendance."""
    
    def __init__(self, db_path="dataset/attendance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the attendance database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status TEXT NOT NULL,
                confidence REAL,
                class_info TEXT,
                section_info TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                total_classes INTEGER DEFAULT 0,
                attended_classes INTEGER DEFAULT 0,
                attendance_percentage REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def mark_attendance(self, student_id, student_name, roll_no, status='Present', 
                       confidence=1.0, class_info='', section_info='', image_path=''):
        """Mark attendance for a student."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current date and time
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')
            
            # Check if attendance already marked for today
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE student_id = ? AND date = ?
            ''', (student_id, date_str))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute('''
                    UPDATE attendance 
                    SET status = ?, confidence = ?, time = ?, class_info = ?, 
                        section_info = ?, image_path = ?
                    WHERE id = ?
                ''', (status, confidence, time_str, class_info, section_info, image_path, existing[0]))
                print(f"Updated attendance for {student_name} on {date_str}")
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO attendance 
                    (student_id, student_name, roll_no, date, time, status, 
                     confidence, class_info, section_info, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, student_name, roll_no, date_str, time_str, 
                      status, confidence, class_info, section_info, image_path))
                print(f"Marked attendance for {student_name} on {date_str}")
            
            # Update student statistics
            self.update_student_stats(student_id, student_name, roll_no)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error marking attendance: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_student_stats(self, student_id, student_name, roll_no):
        """Update student attendance statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Count total classes and attended classes
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_classes,
                    SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as attended_classes
                FROM attendance 
                WHERE student_id = ?
            ''', (student_id,))
            
            result = cursor.fetchone()
            total_classes = result[0] if result[0] else 0
            attended_classes = result[1] if result[1] else 0
            
            # Calculate percentage
            attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0.0
            
            # Update or insert student record
            cursor.execute('''
                INSERT OR REPLACE INTO students 
                (student_id, name, roll_no, total_classes, attended_classes, attendance_percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, student_name, roll_no, total_classes, attended_classes, attendance_percentage))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error updating student stats: {e}")
        finally:
            conn.close()
    
    def get_student_attendance(self, student_id, days=30):
        """Get attendance history for a specific student."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get attendance records for the last 'days' days
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT date, time, status, confidence, class_info, section_info
                FROM attendance 
                WHERE student_id = ? AND date >= ?
                ORDER BY date DESC, time DESC
            ''', (student_id, start_date))
            
            records = cursor.fetchall()
            
            # Get student statistics
            cursor.execute('''
                SELECT name, roll_no, total_classes, attended_classes, attendance_percentage
                FROM students 
                WHERE student_id = ?
            ''', (student_id,))
            
            student_info = cursor.fetchone()
            
            return {
                'student_info': {
                    'student_id': student_id,
                    'name': student_info[0] if student_info else 'Unknown',
                    'roll_no': student_info[1] if student_info else 'Unknown',
                    'total_classes': student_info[2] if student_info else 0,
                    'attended_classes': student_info[3] if student_info else 0,
                    'attendance_percentage': student_info[4] if student_info else 0.0
                },
                'attendance_records': [
                    {
                        'date': record[0],
                        'time': record[1],
                        'status': record[2],
                        'confidence': record[3],
                        'class_info': record[4],
                        'section_info': record[5]
                    }
                    for record in records
                ]
            }
            
        except Exception as e:
            print(f"Error getting student attendance: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_students_summary(self):
        """Get attendance summary for all students."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT student_id, name, roll_no, total_classes, attended_classes, attendance_percentage
                FROM students 
                ORDER BY attendance_percentage DESC
            ''')
            
            students = cursor.fetchall()
            
            return [
                {
                    'student_id': student[0],
                    'name': student[1],
                    'roll_no': student[2],
                    'total_classes': student[3],
                    'attended_classes': student[4],
                    'attendance_percentage': student[5]
                }
                for student in students
            ]
            
        except Exception as e:
            print(f"Error getting students summary: {e}")
            return []
        finally:
            conn.close()
    
    def get_daily_attendance(self, date=None):
        """Get attendance for a specific date."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT student_id, student_name, roll_no, time, status, confidence, class_info, section_info
                FROM attendance 
                WHERE date = ?
                ORDER BY time DESC
            ''', (date,))
            
            records = cursor.fetchall()
            
            return {
                'date': date,
                'total_students': len(records),
                'present_count': len([r for r in records if r[4] == 'Present']),
                'absent_count': len([r for r in records if r[4] == 'Absent']),
                'attendance_records': [
                    {
                        'student_id': record[0],
                        'name': record[1],
                        'roll_no': record[2],
                        'time': record[3],
                        'status': record[4],
                        'confidence': record[5],
                        'class_info': record[6],
                        'section_info': record[7]
                    }
                    for record in records
                ]
            }
            
        except Exception as e:
            print(f"Error getting daily attendance: {e}")
            return None
        finally:
            conn.close()