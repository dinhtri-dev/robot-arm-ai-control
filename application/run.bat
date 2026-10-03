@echo off
echo ============================================
echo  ROBOT CONTROL + AI DETECTION SYSTEM
echo ============================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit
)

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Starting server...
echo.
echo ============================================
echo  Server will start at http://localhost:5000
echo ============================================
echo.

python app.py

pause
