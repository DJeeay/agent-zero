#!/usr/bin/env powershell
# Docker Agent Setup for Presparc
# Run: powershell -ExecutionPolicy Bypass -File setup-docker-agent.ps1

Write-Host ""
Write-Host "Docker Agent Setup - Presparc" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# STEP 1: Verify Docker
Write-Host "[STEP 1/6] Checking Docker..." -ForegroundColor Yellow

try {
    $dockerVersion = docker --version
    Write-Host "  OK: Docker $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Docker not installed" -ForegroundColor Red
    exit 1
}

# STEP 2: Check LLM Models
Write-Host "[STEP 2/6] Checking LLM models..." -ForegroundColor Yellow

$modelPath = "d:\llm_models"
if (Test-Path $modelPath) {
    $models = @(Get-ChildItem $modelPath -Filter "*.gguf" -ErrorAction SilentlyContinue)
    if ($models.Count -gt 0) {
        Write-Host "  OK: Found models" -ForegroundColor Green
        $models | ForEach-Object { Write-Host "     - $($_.Name)" -ForegroundColor Gray }
    } else {
        Write-Host "  WARNING: No GGUF models in $modelPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING: Model path not found: $modelPath" -ForegroundColor Yellow
}

# STEP 3: Create directories
Write-Host "[STEP 3/6] Creating directories..." -ForegroundColor Yellow

$dirs = @("./agent_memory", "./logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  OK: Created $dir" -ForegroundColor Green
    } else {
        Write-Host "  OK: Exists $dir" -ForegroundColor Green
    }
}

# STEP 4: Check files
Write-Host "[STEP 4/6] Checking files..." -ForegroundColor Yellow

$requiredFiles = @("cagent.yaml", "docker-compose-agent.yml", ".env")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $file" -ForegroundColor Red
    }
}

# STEP 5: Environment
Write-Host "[STEP 5/6] Environment setup..." -ForegroundColor Yellow

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "NOTION_API_KEY=sk-" -or $envContent -match "NOTION_API_KEY=[a-zA-Z0-9_-]{20,}") {
        Write-Host "  OK: .env configured" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: .env needs Notion API key" -ForegroundColor Yellow
        Write-Host "     Get from: https://www.notion.so/my-integrations" -ForegroundColor Gray
    }
} else {
    Write-Host "  ERROR: .env missing" -ForegroundColor Red
}

# STEP 6: Next steps
Write-Host "[STEP 6/6] Ready!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env with your Notion API key" -ForegroundColor Gray
Write-Host "  2. Start: docker compose -f docker-compose-agent.yml up -d" -ForegroundColor Gray
Write-Host "  3. View: docker compose -f docker-compose-agent.yml logs -f presparc-agent" -ForegroundColor Gray
Write-Host ""
