@echo off
setlocal enabledelayedexpansion

:: Always set working directory to script location
cd /d "%~dp0"

echo ===================================================
echo   Udaan Society Development Environment Setup
echo ===================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: 2. Check if Virtual Environment exists, if not create and install dependencies
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo [2/4] Installing core dependencies ^(this may take 1-2 minutes on first run^)...
    call .\venv\Scripts\activate.bat
    python -m pip install --upgrade pip --quiet
    
    if exist "requirements.txt" (
        pip install -r requirements.txt
    )
    
    if exist "ai_chatbot\requirements.txt" (
        echo Installing AI Chatbot dependencies...
        pip install -r ai_chatbot\requirements.txt
    )
) else (
    echo [OK] Virtual environment found.
    call .\venv\Scripts\activate.bat
)

:: 3. Run database migrations
echo [3/4] Checking and applying database migrations...
python manage.py migrate --noinput

:: 4. Ensure superuser exists
echo [4/4] Configuring admin user credentials...
python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.filter(username='gyanendra').first(); ( u.set_password('Udaan@123'), u.save() ) if u else User.objects.create_superuser('gyanendra', 'gyanendra@udaansociety.org', 'Udaan@123')" >nul 2>&1

:: 5. Launch Servers in new terminal windows
echo.
echo Launching Django Website (Port 8000)...
start "Django Web Server (Port 8000)" cmd /k "cd /d ""%~dp0"" && .\venv\Scripts\activate && python manage.py runserver 8000"

if exist "ai_chatbot" (
    echo Launching AI Chatbot Backend ^(Port 8001^)...
    start "AI Chatbot Server (Port 8001)" cmd /k "cd /d ""%~dp0ai_chatbot"" && ..\venv\Scripts\activate && uvicorn app.main:app --reload --port 8001"
)

:: 6. Open Browser
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000

echo.
echo ===================================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ===================================================
echo   Website URL     : http://127.0.0.1:8000
echo   Admin Panel URL : http://127.0.0.1:8000/admin/
echo   Chatbot API     : http://127.0.0.1:8001/docs
echo ---------------------------------------------------
echo   Admin Username  : gyanendra
echo   Admin Password  : Udaan@123
echo ===================================================
echo (Keep the opened server terminal windows running. Close them to stop.)
echo.
pause
