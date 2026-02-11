
Write-Host "Starting Insurance SaaS Platform..." -ForegroundColor Green
$currentDir = Get-Location

# 1. Start Main Backend (Port 8000)
Write-Host "Starting Backend API..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir/backend'; python -m app.main"

# 2. Start Agent Mesh
Write-Host "Starting AI Agent Mesh..." -ForegroundColor Cyan
# Re-using the logic from start_mesh.ps1 but inline to ensure paths work from root
$agents = @(
    @{ Name = "Orchestrator"; Path = "backend/agents/a2a_multi_ai_agents/__main__.py"; Port = 33335 },
    @{ Name = "Claims Agent"; Path = "backend/agents/a2a_claims_agent/__main__.py"; Port = 33333 },
    @{ Name = "Quote Agent"; Path = "backend/agents/a2a_quote_agent/__main__.py"; Port = 8020 },
    @{ Name = "Policy Agent"; Path = "backend/agents/a2a_policy_agent/__main__.py"; Port = 8021 }
)

foreach ($agent in $agents) {
    $fullPath = Join-Path $currentDir $agent.Path
    if (Test-Path $fullPath) {
        Write-Host "Launching $($agent.Name) on port $($agent.Port)..." -ForegroundColor Yellow
        # Start minimized to avoid clutter, with absolute PYTHONPATH
        $modulePath = ($agent.Path -replace "^backend/", "" -replace "/__main__\.py$", "" -replace "/", ".")
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$currentDir/backend'; `$env:PORT='$($agent.Port)'; python -m $modulePath"
    }
    else {
        Write-Host "Error: Could not find $($agent.Name) at $fullPath" -ForegroundColor Red
    }
}

# 3. Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir/frontend'; npm run dev"

Write-Host "All services launching." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
Write-Host "Claims Agent: http://localhost:8019"
Write-Host "Please wait a few moments for services to initialize."
