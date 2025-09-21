@echo off
echo Setting up AI Attendance System Backend...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create uploads directory
echo Creating uploads directory...
if not exist "uploads" mkdir uploads
if not exist "uploads\face_images" mkdir uploads\face_images

REM Initialize database
echo Initializing database...
python -c "from app.models import create_tables; create_tables()"

REM Seed database with sample data
echo Seeding database with sample data...
cd ..\database
python seed_data.py
cd ..\backend

echo Backend setup completed!
echo.
echo To start the backend server, run:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
pause