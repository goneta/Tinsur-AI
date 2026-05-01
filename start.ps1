Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TINSUR-AI - Starting Application" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"

# Start Backend in a new terminal
Write-Host "[1/2] Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; pip install -r requirements.txt; python create_admin.py; python run_server.py" -WindowStyle Normal

Write-Host "  Waiting 8 seconds for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Start Frontend in a new terminal
Write-Host "[2/2] Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; npm install; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Both servers are starting!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Admin Login:" -ForegroundColor Cyan
Write-Host "    Email: admin@demoinsurance.com" -ForegroundColor White
Write-Host "    Password: Admin123!" -ForegroundColor White
Write-Host ""
Write-Host "  Existing Client:" -ForegroundColor Cyan
Write-Host "    Email: guil6c@gmail.com" -ForegroundColor White
Write-Host "    (use existing password)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Wait ~30 seconds for both servers to fully start," -ForegroundColor Yellow
Write-Host "  then open http://localhost:3000 in your browser." -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Green
