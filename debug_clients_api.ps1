
$loginUrl = "http://localhost:8000/api/v1/auth/login"
$clientUrl = "http://localhost:8000/api/v1/clients?limit=100"

# 1. Login
$body = @{
    email    = "admin@demoinsurance.com"
    password = "admin123"
} | ConvertTo-Json

try {
    Write-Host "Logging in..."
    $response = Invoke-RestMethod -Method Post -Uri $loginUrl -Body $body -ContentType "application/json"
    $token = $response.access_token
    Write-Host "Login Successful. Token acquired: $token"
    if ([string]::IsNullOrEmpty($token)) {
        Write-Host "❌ Token is EMPTY!"
        exit
    }
    Write-Host "Login Successful. Token acquired."
}
catch {
    Write-Host "Login Failed:" $_.Exception.Message
    Write-Host $_.ErrorDetails.Message
    exit
}

# 2. Get Clients
try {
    Write-Host "Fetching Clients..."
    $headers = @{ "Authorization" = "Bearer $token" }
    $clients = Invoke-RestMethod -Method Get -Uri $clientUrl -Headers $headers -ContentType "application/json"
    
    if ($clients.Count -eq 0) {
        Write-Host "⚠️  Client List is EMPTY."
    }
    else {
        Write-Host "✅ Found $($clients.Count) clients."
        $clients | Format-Table id, first_name, last_name, company_id
    }
}
catch {
    Write-Host "Fetch Clients Failed:" $_.Exception.Message
    Write-Host $_.ErrorDetails.Message
}
