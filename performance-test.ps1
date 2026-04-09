# Performance testing script for OpenAgents agents
$Results = @()

Write-Host "=== OpenAgents Performance Test ===" -ForegroundColor Green

# Test Hermes agents
Write-Host "`nTesting Hermes agents..." -ForegroundColor Yellow
$env:OPENAI_BASE_URL = "http://localhost:9000/v1"
$env:OPENAI_API_KEY = "dummy"
$env:NANOCLAW_MODEL = "hermes-3"

$TestPrompts = @(
    "Hello",
    "What is 2+2?",
    "Explain photosynthesis in one sentence",
    "Write a Python function that adds two numbers",
    "Summarize the history of artificial intelligence"
)

foreach ($prompt in $TestPrompts) {
    Write-Host "Testing: $prompt" -ForegroundColor Cyan
    
    $start = Get-Date
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:9000/v1/chat/completions" -Method POST -ContentType "application/json" -Body @{
            model = "hermes-3"
            messages = @(@{role = "user"; content = $prompt})
            max_tokens = 200
        } -TimeoutSec 60
        
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        $Results += [PSCustomObject]@{
            Agent = "hermes-3"
            Prompt = $prompt
            ResponseTime = $duration
            PromptTokens = $response.usage.prompt_tokens
            CompletionTokens = $response.usage.completion_tokens
            TotalTokens = $response.usage.total_tokens
            TokensPerSec = [math]::Round($response.usage.completion_tokens / ($duration / 1000), 2)
            Status = "Success"
        }
        
        Write-Host "  Response: $($response.choices[0].message.content.Substring(0, [math]::Min(50, $response.choices[0].message.content.Length)))..." -ForegroundColor Green
        Write-Host "  Time: $([math]::Round($duration, 2))ms | Tokens: $($response.usage.total_tokens) | Rate: $([math]::Round($response.usage.completion_tokens / ($duration / 1000), 2)) t/s" -ForegroundColor Gray
    }
    catch {
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        $Results += [PSCustomObject]@{
            Agent = "hermes-3"
            Prompt = $prompt
            ResponseTime = $duration
            PromptTokens = 0
            CompletionTokens = 0
            TotalTokens = 0
            TokensPerSec = 0
            Status = "Error: $($_.Exception.Message)"
        }
        
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

# Test Nemotron agent
Write-Host "`nTesting Nemotron agent..." -ForegroundColor Yellow
$env:OPENAI_BASE_URL = "http://localhost:1234/v1"
$env:OPENAI_API_KEY = "dummy"
$env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"

foreach ($prompt in $TestPrompts) {
    Write-Host "Testing: $prompt" -ForegroundColor Cyan
    
    $start = Get-Date
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:1234/v1/chat/completions" -Method POST -ContentType "application/json" -Body @{
            model = "nvidia-nemotron-3-nano-4b"
            messages = @(@{role = "user"; content = $prompt})
            max_tokens = 200
        } -TimeoutSec 60
        
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        $Results += [PSCustomObject]@{
            Agent = "nemotron-3-nano"
            Prompt = $prompt
            ResponseTime = $duration
            PromptTokens = $response.usage.prompt_tokens
            CompletionTokens = $response.usage.completion_tokens
            TotalTokens = $response.usage.total_tokens
            TokensPerSec = [math]::Round($response.usage.completion_tokens / ($duration / 1000), 2)
            Status = "Success"
        }
        
        Write-Host "  Response: $($response.choices[0].message.content.Substring(0, [math]::Min(50, $response.choices[0].message.content.Length)))..." -ForegroundColor Green
        Write-Host "  Time: $([math]::Round($duration, 2))ms | Tokens: $($response.usage.total_tokens) | Rate: $([math]::Round($response.usage.completion_tokens / ($duration / 1000), 2)) t/s" -ForegroundColor Gray
    }
    catch {
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        
        $Results += [PSCustomObject]@{
            Agent = "nemotron-3-nano"
            Prompt = $prompt
            ResponseTime = $duration
            PromptTokens = 0
            CompletionTokens = 0
            TotalTokens = 0
            TokensPerSec = 0
            Status = "Error: $($_.Exception.Message)"
        }
        
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

# Generate report
Write-Host "`n=== PERFORMANCE REPORT ===" -ForegroundColor Green
Write-Host "Agent         | Avg Time (ms) | Tokens/sec | Success Rate" -ForegroundColor White
Write-Host "--------------|---------------|------------|-------------" -ForegroundColor White

$grouped = $Results | Group-By Agent
foreach ($group in $grouped) {
    $successful = $group.Group | Where-Object { $_.Status -eq "Success" }
    $avgTime = [math]::Round(($successful | Measure-Object -Property ResponseTime -Average).Average, 2)
    $avgTokensPerSec = [math]::Round(($successful | Measure-Object -Property TokensPerSec -Average).Average, 2)
    $successRate = [math]::Round(($successful.Count / $group.Group.Count) * 100, 1)
    
    Write-Host ("{0,-14} | {1,-13} | {2,-10} | {3,-11}" -f $group.Name, $avgTime, $avgTokensPerSec, "$successRate%") -ForegroundColor Cyan
}

# Export results
$Results | Export-Csv -Path "d:\openagents\performance-results.csv" -NoTypeInformation
Write-Host "`nResults exported to: d:\openagents\performance-results.csv" -ForegroundColor Green

# Detailed analysis
Write-Host "`n=== DETAILED ANALYSIS ===" -ForegroundColor Green
$grouped | ForEach-Object {
    Write-Host "`n$($_.Name) Performance:" -ForegroundColor Yellow
    $successful = $_.Group | Where-Object { $_.Status -eq "Success" }
    
    if ($successful.Count -gt 0) {
        $fastest = $successful | Sort-Object ResponseTime | Select-Object -First 1
        $slowest = $successful | Sort-Object ResponseTime -Descending | Select-Object -First 1
        $highestRate = $successful | Sort-Object TokensPerSec -Descending | Select-Object -First 1
        
        Write-Host "  Fastest: $($fastest.Prompt) - $([math]::Round($fastest.ResponseTime, 2))ms" -ForegroundColor Gray
        Write-Host "  Slowest: $($slowest.Prompt) - $([math]::Round($slowest.ResponseTime, 2))ms" -ForegroundColor Gray
        Write-Host "  Highest rate: $($highestRate.Prompt) - $($highestRate.TokensPerSec) t/s" -ForegroundColor Gray
        Write-Host "  Average tokens per response: $([math]::Round(($successful | Measure-Object -Property TotalTokens -Average).Average, 1))" -ForegroundColor Gray
    }
}
