# Start Agent Zero Natively on Windows
Write-Host "🚀 STARTING AGENT ZERO NATIVELY..." -ForegroundColor Cyan

# 1. Environment
$env:PYTHONPATH = $PWD
$python = ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "❌ Virtual environment not found. Please run 'uv venv' first." -ForegroundColor Red
    exit
}

# 2. Check Ollama
Write-Host "🔍 Checking Ollama..." -ForegroundColor Yellow
$ollamaList = ollama list
if ($ollamaList -match "hermes-3-8b") {
    Write-Host "✅ Model 'hermes-3-8b' is ready!" -ForegroundColor Green
} else {
    Write-Host "⏳ Model 'hermes-3-8b' not found yet. Attempting to start anyway..." -ForegroundColor Yellow
}

# 3. Start UI
Write-Host "🌐 Starting Agent Zero Web UI..." -ForegroundColor Green
$env:PYTHONPATH = $PWD
& "$PWD\.venv\Scripts\python.exe" run_ui.py
