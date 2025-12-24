

$env:PYTHONPATH = "$PWD\backend"
Write-Host "Set PYTHONPATH to: $env:PYTHONPATH"

$agents = @(
    @{ Name = "Orchestrator"; Path = "backend/agents/a2a_multi_ai_agents/__main__.py"; Port = 8025 },
    @{ Name = "Claims Agent"; Path = "backend/agents/a2a_claims_agent/__main__.py"; Port = 8019 },
    @{ Name = "Quote Agent"; Path = "backend/agents/a2a_quote_agent/__main__.py"; Port = 8020 },
    @{ Name = "Policy Agent"; Path = "backend/agents/a2a_policy_agent/__main__.py"; Port = 8021 },
    @{ Name = "Memory Agent"; Path = "backend/agents/a2a_persistent_storage_agent/__main__.py"; Port = 8031 }
)

Write-Host "Starting Agent Mesh..." -ForegroundColor Cyan

foreach ($agent in $agents) {
    Write-Host "Starting $($agent.Name) on port $($agent.Port)..."
    Start-Process python -ArgumentList $agent.Path -WindowStyle Minimized
}

Write-Host "All agents started. Waiting 10 seconds for initialization..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "Mesh is ready!" -ForegroundColor Green
