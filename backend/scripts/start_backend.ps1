
Write-Host "Starting Main Backend on Port 8000..."
Set-Location "$PSScriptRoot\.."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
