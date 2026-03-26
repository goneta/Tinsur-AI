
Write-Host "Stopping existing Python agents..." -ForegroundColor Yellow
Stop-Process -Name "python" -ErrorAction SilentlyContinue

Write-Host "Waiting 2 seconds..."
Start-Sleep -Seconds 2

& "$PSScriptRoot\start_mesh.ps1"
