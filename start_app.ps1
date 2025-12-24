# Startup Script for Insurance SaaS
# Launches Backend and Frontend in separate windows

Write-Host "Starting Insurance SaaS..." -ForegroundColor Green

# Start Backend
Write-Host "Launching Backend (Port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; $env:PYTHONPATH='.'; python -m uvicorn app.main:app --reload --port 8000"

# Start Frontend
Write-Host "Launching Frontend (Port 3000)..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Services started! Backend at http://localhost:8000/docs, Frontend at http://localhost:3000" -ForegroundColor Green
