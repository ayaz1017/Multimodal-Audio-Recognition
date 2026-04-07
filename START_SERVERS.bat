@echo off
echo ===================================================================
echo Multimodal Audio Recognition - Starting Both Servers
echo ===================================================================
echo.

REM Open backend in first terminal
echo Starting Backend Server...
start cmd /k "cd /d %cd%\backend && python app.py"

REM Wait for backend to initialize
timeout /t 3 /nobreak

REM Open frontend in second terminal
echo Starting Frontend Server...
start cmd /k "cd /d %cd%\frontend && npm start"

echo.
echo ===================================================================
echo Servers starting:
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo ===================================================================
echo Press Ctrl+C in either terminal to stop the respective server
pause
