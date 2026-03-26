@echo off
cd C:\THUNDERFAM APPS\tinsur-ai
echo Starting Tinsur-AI Frontend...
echo.
echo The application will be available at:
echo   http://localhost:3000
echo.
echo Compiling... (this may take 30-60 seconds on first run)
echo.
npm run dev --workspace=tinsur-ai-frontend
pause
