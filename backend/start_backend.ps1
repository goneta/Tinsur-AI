
$currentDir = Get-Location
Write-Host "Starting Insurance SaaS Backend Services..." -ForegroundColor Green

# Start Main Backend
Write-Host "Starting Main API (Port 8000)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; python -m app.main"

# Start Claims Agent
Write-Host "Starting Claims Agent (Port 8019)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; python agents/a2a_claims_agent/__main__.py"

Write-Host "Services started in new windows."
Write-Host "Ensure the Frontend is running with: npm run dev"
