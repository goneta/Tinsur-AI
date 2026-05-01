@echo off
echo ============================================
echo   TINSUR-AI - Starting Application
echo ============================================
echo.

:: Start Backend
echo [1/2] Starting Backend Server (FastAPI on port 8000)...
cd /d "%~dp0backend"
start "Tinsur-AI Backend" cmd /k "pip install -r requirements.txt && python create_admin.py && python run_server.py"

:: Wait for backend to initialize
echo Waiting 10 seconds for backend to start...
timeout /t 10 /nobreak >nul

:: Clean and start Frontend
echo [2/2] Starting Frontend Server (Next.js on port 3000)...
cd /d "%~dp0"
echo Cleaning old node_modules to avoid stale cache...
if exist "node_modules" rmdir /s /q "node_modules" 2>nul
if exist "frontend\node_modules" rmdir /s /q "frontend\node_modules" 2>nul
if exist "frontend\.next" rmdir /s /q "frontend\.next" 2>nul
start "Tinsur-AI Frontend" cmd /k "npm install && npm run dev"

echo.
echo ============================================
echo   Both servers are starting!
echo ============================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Admin Login:
echo     Email: admin@demoinsurance.com
echo     Password: Admin123!
echo.
echo   Wait ~60 seconds for npm install + servers to start,
echo   then open http://localhost:3000 in your browser.
echo ============================================
pause
