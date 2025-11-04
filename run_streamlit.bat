@echo off
REM Cross-platform Streamlit startup script for Windows

echo.
echo ============================================
echo   Excel Map Coordinates Converter
echo   Streamlit Version
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

REM Run Streamlit app
echo.
echo [SUCCESS] Starting Streamlit server...
echo.
echo ========================================
echo   The app will open in your browser
echo   Press Ctrl+C to stop
echo ========================================
echo.

streamlit run app.py

pause
