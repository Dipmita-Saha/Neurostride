@echo off
echo Installing NeuroStride Dependencies...
echo.

echo [1/2] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install backend dependencies
    echo Please ensure Python and pip are installed and accessible
    pause
    exit /b 1
)
cd ..

echo.
echo [2/2] Creating models directory...
if not exist "backend\models" mkdir "backend\models"

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Run start.bat to launch the application
echo 2. Open http://localhost:8080 in your browser
echo.
pause