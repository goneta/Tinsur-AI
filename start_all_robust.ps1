
# Start-All-Services-Robust.ps1
# Robust startup script that cleans up ports and starts services based on a centralized registry.

$ErrorActionPreference = "Continue"

# Define Paths
$BasePath = "C:\Users\user\Desktop\Insurance SaaS"
$BackendPath = Join-Path $BasePath "backend"
$FrontendPath = Join-Path $BasePath "frontend"
$LogPath = Join-Path $BasePath "logs"
$RegistryPath = Join-Path $BackendPath "agent_registry.json"

# Ensure Log Directory Exists
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath | Out-Null
}

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMsg = "[$Timestamp] $Message"
    Write-Host $LogMsg -ForegroundColor Cyan
    Add-Content -Path (Join-Path $LogPath "startup.log") -Value $LogMsg
}

function Kill-Port {
    param([int]$Port)
    $ProcessLines = netstat -ano | Select-String ":$Port"
    foreach ($Line in $ProcessLines) {
        $Parts = $Line.ToString().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
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

# 1. Cleanup Phase
Write-Log "Starting System Cleanup..."
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
        Write-Log "Error reading registry during cleanup: $_"
    }
}
else {
    Write-Log "CRITICAL: Agent registry not found at $RegistryPath"
    exit 1
}

Kill-Port 3000 # Frontend

# 2. Start Main Backend
Write-Log "Starting Main Backend API on Port 8000..."
$BackendProcess = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory $BackendPath -PassThru -NoNewWindow
Start-Sleep -Seconds 5

# 3. Start Agent Mesh (Dynamic Loop)
Write-Log "Starting Agent Mesh..."

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
            # Note: We assume the agent uses the port passed in the file or code. 
            # Ideally, we should pass the port as an env var or argument, but your agents currently hardcode it in __main__.py.
            # To fix port conflicts accurately, we rely on the __main__.py matching the registry. 
            # If they differ, we might have issues.
            # Future improvement: Update agents to read PORT from env.
            
            Start-Process -FilePath "python" -ArgumentList "$WinPath" -WorkingDirectory $BackendPath -WindowStyle Minimized
            Start-Sleep -Seconds 2
        }
        else {
            Write-Log "WARNING: Script for $AgentName not found at $FullAgentPath"
        }
    }
}

# 4. Start Frontend
Write-Log "Starting Frontend on Port 3000..."
$FrontendProcess = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $FrontendPath -PassThru -NoNewWindow

Write-Log "All services initiated. Check specific logs for details."
Write-Host "Press Ctrl+C to stop the script (note: background processes may persist)."
