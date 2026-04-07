@echo off
echo =========================================
echo Multimodal Audio Recognition - Setup
echo =========================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python not found. Please install Python 3.8+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK Found: Python %PYTHON_VERSION%

REM Check Node.js
echo.
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Node.js not found. Please install Node.js 14+
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo OK Found: Node %NODE_VERSION%

REM Backend setup
echo.
echo =========================================
echo Setting up Backend
echo =========================================
echo Installing backend dependencies...
pip install -r backend_requirements.txt

if not exist "saved_model\audio_model_full.h5" if not exist "saved_model\audio_model.h5" if not exist "saved_model\audio_model.pt" (
    echo.
    echo WARNING: Model file not found in saved_model/
    echo Expected one of: audio_model_full.h5, audio_model.h5, audio_model.pt
)

REM Frontend setup
echo.
echo =========================================
echo Setting up Frontend
echo =========================================
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To run the application:
echo.
echo 1. Start Backend (in project root):
echo    python backend/app.py
echo.
echo 2. Start Frontend (in another terminal):
echo    cd frontend ^&^& npm start
echo.
echo Then open http://localhost:3000 in your browser
echo.
pause
