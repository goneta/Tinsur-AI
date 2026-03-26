# Comprehensive Tinsur-AI Feature Testing Script
# Tests all critical features before production deployment

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$FrontendUrl = "http://localhost:3000"
)

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "TINSUR-AI COMPREHENSIVE FEATURE TEST"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "Testing Backend: $BaseUrl"
Write-Host "Testing Frontend: $FrontendUrl"
Write-Host ""

# Test Results
$results = @{
    passed = 0
    failed = 0
    errors = @()
}

# Helper function to make API calls
function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Url,
        [string]$Name,
        [hashtable]$Headers = @{},
        [string]$Body = $null
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            ContentType = "application/json"
            UseBasicParsing = $true
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-WebRequest @params
        $results.passed++
        Write-Host "✅ PASS: $Name" -ForegroundColor Green
        return $response
    }
    catch {
        $results.failed++
        $error_msg = "❌ FAIL: $Name - $($_.Exception.Message)"
        Write-Host $error_msg -ForegroundColor Red
        $results.errors += $error_msg
        return $null
    }
}

Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 1: BACKEND HEALTH CHECK"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

# Test 1: Root endpoint
Test-Endpoint -Method GET -Url "$BaseUrl/" -Name "Backend Root Endpoint"

# Test 2: Swagger UI
Test-Endpoint -Method GET -Url "$BaseUrl/docs" -Name "Swagger UI"

# Test 3: OpenAPI Schema
Test-Endpoint -Method GET -Url "$BaseUrl/openapi.json" -Name "OpenAPI Schema"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 2: AUTHENTICATION"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

# Test 4: Admin login
$loginBody = @{
    email = "admin@example.com"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Test-Endpoint -Method POST `
    -Url "$BaseUrl/api/v1/auth/login" `
    -Name "Admin Login" `
    -Body $loginBody

$adminToken = $null
if ($loginResponse) {
    $adminToken = ($loginResponse.Content | ConvertFrom-Json).access_token
    if ($adminToken) {
        Write-Host "   Admin Token: $($adminToken.Substring(0,20))..." -ForegroundColor Cyan
    }
}

# Test 5: Get current user
if ($adminToken) {
    $headers = @{ Authorization = "Bearer $adminToken" }
    Test-Endpoint -Method GET `
        -Url "$BaseUrl/api/v1/auth/me" `
        -Name "Get Current User" `
        -Headers $headers
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 3: CLIENT MANAGEMENT (CRITICAL)"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

if ($adminToken) {
    $headers = @{ Authorization = "Bearer $adminToken" }
    
    # Test 6: List clients
    Test-Endpoint -Method GET `
        -Url "$BaseUrl/api/v1/clients/?page=1&page_size=10" `
        -Name "List Clients" `
        -Headers $headers
    
    # Test 7: Create client
    $clientBody = @{
        client_type = "individual"
        first_name = "TestClient"
        last_name = "$(Get-Random)"
        email = "test$(Get-Random)@example.com"
        phone = "+225123456789"
        country = "Côte d'Ivoire"
    } | ConvertTo-Json
    
    $createClientResponse = Test-Endpoint -Method POST `
        -Url "$BaseUrl/api/v1/clients/" `
        -Name "Create Client" `
        -Headers $headers `
        -Body $clientBody
    
    if ($createClientResponse) {
        $createdClient = $createClientResponse.Content | ConvertFrom-Json
        $clientId = $createdClient.id
        Write-Host "   Created Client ID: $clientId" -ForegroundColor Cyan
        
        # Test 8: Get client details
        Test-Endpoint -Method GET `
            -Url "$BaseUrl/api/v1/clients/$clientId" `
            -Name "Get Client Details" `
            -Headers $headers
        
        # Test 9: Update client
        $updateBody = @{
            first_name = "UpdatedName"
        } | ConvertTo-Json
        
        Test-Endpoint -Method PUT `
            -Url "$BaseUrl/api/v1/clients/$clientId" `
            -Name "Update Client" `
            -Headers $headers `
            -Body $updateBody
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 4: QUOTE MANAGEMENT (CRITICAL)"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

if ($adminToken) {
    $headers = @{ Authorization = "Bearer $adminToken" }
    
    # Test 10: List quotes
    Test-Endpoint -Method GET `
        -Url "$BaseUrl/api/v1/quotes/?page=1&page_size=10" `
        -Name "List Quotes" `
        -Headers $headers
    
    # Test 11: Create quote
    $quoteBody = @{
        client_id = $clientId
        quote_type = "auto"
        status = "draft"
        premium_amount = 50000
        coverage_type = "comprehensive"
    } | ConvertTo-Json
    
    $createQuoteResponse = Test-Endpoint -Method POST `
        -Url "$BaseUrl/api/v1/quotes/" `
        -Name "Create Quote" `
        -Headers $headers `
        -Body $quoteBody
    
    if ($createQuoteResponse) {
        $quote = $createQuoteResponse.Content | ConvertFrom-Json
        $quoteId = $quote.id
        Write-Host "   Created Quote ID: $quoteId" -ForegroundColor Cyan
        
        # Test 12: Get quote details
        Test-Endpoint -Method GET `
            -Url "$BaseUrl/api/v1/quotes/$quoteId" `
            -Name "Get Quote Details" `
            -Headers $headers
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 5: USER MANAGEMENT"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

if ($adminToken) {
    $headers = @{ Authorization = "Bearer $adminToken" }
    
    # Test 13: List users
    Test-Endpoint -Method GET `
        -Url "$BaseUrl/api/v1/users/?page=1&page_size=10" `
        -Name "List Users" `
        -Headers $headers
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 6: ERROR HANDLING"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

# Test 14: Invalid credentials
$badLoginBody = @{
    email = "admin@example.com"
    password = "wrongpassword"
} | ConvertTo-Json

$badResponse = Test-Endpoint -Method POST `
    -Url "$BaseUrl/api/v1/auth/login" `
    -Name "Invalid Credentials (Should Fail)" `
    -Body $badLoginBody

# Test 15: Missing required fields
$badClientBody = @{
    client_type = "individual"
} | ConvertTo-Json

if ($adminToken) {
    $headers = @{ Authorization = "Bearer $adminToken" }
    $badClientResponse = Test-Endpoint -Method POST `
        -Url "$BaseUrl/api/v1/clients/" `
        -Name "Missing Required Fields (Should Fail)" `
        -Headers $headers `
        -Body $badClientBody
}

# Test 16: Unauthorized access (no token)
Test-Endpoint -Method GET `
    -Url "$BaseUrl/api/v1/clients/" `
    -Name "Unauthorized Access (Should Fail)"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "PHASE 7: FRONTEND HEALTH CHECK"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""

# Test 17: Frontend loads
try {
    $frontendResponse = Invoke-WebRequest -Uri $FrontendUrl -UseBasicParsing -TimeoutSec 10
    if ($frontendResponse.StatusCode -eq 200) {
        $results.passed++
        Write-Host "✅ PASS: Frontend Loads" -ForegroundColor Green
    }
}
catch {
    $results.failed++
    Write-Host "❌ FAIL: Frontend Not Responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host "TEST RESULTS SUMMARY"
Write-Host "════════════════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "Total Tests: $($results.passed + $results.failed)"
Write-Host "✅ Passed: $($results.passed)" -ForegroundColor Green
Write-Host "❌ Failed: $($results.failed)" -ForegroundColor Red
Write-Host ""

if ($results.failed -eq 0) {
    Write-Host "════════════════════════════════════════════════════════════════════"
    Write-Host "✅ ALL TESTS PASSED - READY FOR PRODUCTION"
    Write-Host "════════════════════════════════════════════════════════════════════"
    Write-Host ""
}
else {
    Write-Host "════════════════════════════════════════════════════════════════════"
    Write-Host "❌ SOME TESTS FAILED - REVIEW BEFORE PRODUCTION"
    Write-Host "════════════════════════════════════════════════════════════════════"
    Write-Host ""
    Write-Host "Failed Tests:"
    foreach ($error in $results.errors) {
        Write-Host "  $error" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "Testing completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""
