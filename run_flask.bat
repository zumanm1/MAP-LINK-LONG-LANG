@echo off
REM Cross-platform Flask startup script for Windows

echo.
echo ============================================
echo   Excel Map Coordinates Converter
echo   Flask Version
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -q -r requirements.txt

REM Create required directories
if not exist "uploads" mkdir uploads
if not exist "processed" mkdir processed

REM Run Flask app
echo.
echo [SUCCESS] Starting Flask server...
echo.
echo ========================================
echo   Access the app at: http://localhost:5000
echo   Press Ctrl+C to stop
echo ========================================
echo.

python flask_app.py

pause
