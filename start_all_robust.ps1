
# Start-All-Services-Robust.ps1
# Robust startup script that cleans up ports and starts services based on a centralized registry.

$ErrorActionPreference = "Continue"

# Define Paths
$BasePath = "C:\Users\user\Desktop\Tinsur.AI"
$BackendPath = Join-Path $BasePath "backend"
$FrontendPath = Join-Path $BasePath "frontend"
$LogPath = Join-Path $BasePath "logs"
$RegistryPath = Join-Path $BackendPath "agent_registry.json"

# Ensure Log Directory Exists
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Color = "Cyan")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMsg = "[$Timestamp] $Message"
    Write-Host $LogMsg -ForegroundColor $Color
    Add-Content -Path (Join-Path $LogPath "startup.log") -Value $LogMsg
}

function Kill-Port {
    param([int]$Port)
    $ProcessLines = netstat -ano | Select-String ":$Port "
    foreach ($Line in $ProcessLines) {
        $Parts = $Line.ToString().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
        if ($Parts[1].EndsWith(":$Port")) {
            $PidVal = $Parts[-1]
            Write-Log "Killing process $PidVal on port $Port"
            try {
                Stop-Process -Id $PidVal -Force -ErrorAction SilentlyContinue
            }
            catch {
                Write-Log "Could not kill process $PidVal (might be already gone)"
            }
        }
    }
}

function Wait-For-Port {
    param([int]$Port, [int]$TimeoutSeconds = 10)
    $Start = Get-Date
    while (((Get-Date) - $Start).TotalSeconds -lt $TimeoutSeconds) {
        if (Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

# 1. Cleanup Phase
Write-Log "Starting System Cleanup..." -Color Yellow
Kill-Port 8000 # Main API

# Load Registry
if (Test-Path $RegistryPath) {
    try {
        $RegistryJson = Get-Content -Path $RegistryPath -Raw | ConvertFrom-Json
        foreach ($Agent in $RegistryJson) {
            if ($Agent.enabled) {
                Kill-Port $Agent.port
            }
        }
    }
    catch {
        Write-Log "Error reading registry during cleanup: $_" -Color Red
    }
}
else {
    Write-Log "CRITICAL: Agent registry not found at $RegistryPath" -Color Red
    exit 1
}

Kill-Port 3000 # Frontend

# 2. Start Main Backend
Write-Log "Starting Main Backend API on Port 8000..."
$BackendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "$env:PYTHONPATH='.'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory $BackendPath -PassThru
if (Wait-For-Port 8000) {
    Write-Log "Main Backend API is UP." -Color Green
} else {
    Write-Log "WARNING: Main Backend API failed to start within timeout." -Color Red
}

# 3. Start Agent Mesh (Dynamic Loop)
Write-Log "Starting Agent Mesh..." -Color Yellow

foreach ($Agent in $RegistryJson) {
    if ($Agent.enabled) {
        $AgentName = $Agent.name
        $AgentPort = $Agent.port
        $AgentPath = $Agent.path
        
        # Convert path separators for Windows
        $WinPath = $AgentPath -replace "/", "\"
        $FullAgentPath = Join-Path $BackendPath $WinPath
        
        if (Test-Path $FullAgentPath) {
            Write-Log "Starting $AgentName on port $AgentPort..."
            
            # Start agent in a new minimized window
            Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "$env:PYTHONPATH='.'; python $WinPath" -WorkingDirectory $BackendPath -WindowStyle Minimized
            
            if (Wait-For-Port $AgentPort) {
                Write-Log "$AgentName is UP on port $AgentPort." -Color Green
            } else {
                Write-Log "WARNING: $AgentName failed to start on port $AgentPort within timeout." -Color Red
            }
        }
        else {
            Write-Log "WARNING: Script for $AgentName not found at $FullAgentPath" -Color Red
        }
    }
}

# 4. Start Frontend
Write-Log "Starting Frontend on Port 3000..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "npm run dev" -WorkingDirectory $FrontendPath -WindowStyle Minimized

if (Wait-For-Port 3000) {
    Write-Log "Frontend is UP on port 3000." -Color Green
} else {
    Write-Log "WARNING: Frontend failed to start on port 3000 within timeout." -Color Red
}

Write-Log "All services initiated. Check specific logs for details." -Color Green
Write-Host "Startup complete. Background processes are running in separate windows." -ForegroundColor Green
