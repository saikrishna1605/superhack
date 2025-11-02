@echo off
echo Starting PulseOps Local Development Servers...
echo.

REM Start Backend API
echo Starting Backend API on port 8000...
start "PulseOps Backend API" powershell -NoExit -Command "cd 'd:\SuperOps-Hackathon\pulseops\services\api'; python -m uvicorn main:app --reload --port 8000"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Frontend UI  
echo Starting Frontend UI on port 3000...
start "PulseOps Frontend UI" powershell -NoExit -Command "cd 'd:\SuperOps-Hackathon\pulseops\services\ui'; npm start"

REM Wait for servers to start
timeout /t 30 /nobreak

REM Open browser
echo Opening browser...
start chrome "http://localhost:3000"

echo.
echo ========================================
echo PulseOps Servers Started!
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo.
echo Login: it@pulseops.com / itadmin123
echo.
echo Close this window when done.
pause
