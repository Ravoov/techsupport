@echo off
echo ============================================
echo     STARTING FULL SUPPORT SYSTEM (LOCAL)
echo ============================================

REM -------------------------------
REM START BACKEND (Flask API)
REM -------------------------------
echo.
echo Starting Backend API...
start cmd /k "cd backend && python app.py"

REM -------------------------------
REM START FRONTEND (HTML/JS)
REM -------------------------------
echo.
echo Starting Frontend (Python HTTP Server)...
start cmd /k "cd frontend && python -m http.server 5500"

REM -------------------------------
REM START DASHBOARD (Python GUI)
REM -------------------------------
echo.
echo Starting Dashboard GUI...
start cmd /k "cd dashboard && python dashboard.py"

echo.
echo ============================================
echo   All services launched in separate windows
echo ============================================
pause