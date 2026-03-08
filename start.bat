@echo off
echo Starting NeuroStride Application...
echo.

echo [1/2] Starting Backend Server...
cd backend
start "NeuroStride Backend" cmd /k "python app.py"
cd ..

echo [2/2] Starting Frontend Server...
timeout /t 3 /nobreak > nul
cd frontend
start "NeuroStride Frontend" cmd /k "python serve.py"
cd ..

echo.
echo NeuroStride is starting up!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:8080
echo.
echo Press any key to exit...
pause > nul