@echo off
echo Installing PyQt5 Desktop App Requirements...
echo.

REM Navigate to desktop app directory
cd /d "%~dp0"

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run the application:
echo python main.py
echo.
pause