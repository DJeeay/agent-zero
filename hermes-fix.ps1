# Script pour corriger le problème Hermes - retour à l'adaptateur original
Write-Host "=== CORRECTION HERMES ===" -ForegroundColor Green

# Configurer les variables pour Hermes
$env:OPENAI_BASE_URL = "http://localhost:9000/v1"
if (-not $env:OPENAI_API_KEY) { $env:OPENAI_API_KEY = "lm-studio" }
$env:NANOCLAW_MODEL = "hermes-3"

Write-Host "Configuration Hermes mise à jour" -ForegroundColor Cyan

# Redémarrer le daemon avec les bonnes variables
Write-Host "Redémarrage du daemon..." -ForegroundColor Yellow
agn down
agn up -d

Write-Host "Test de l'adaptateur Hermes..." -ForegroundColor Yellow

# Test de l'adaptateur
try {
    $body = @{
        model = "hermes-3"
        messages = @(@{role = "user"; content = "Bonjour"})
        max_tokens = 50
        temperature = 0.7
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:9000/v1/chat/completions" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "Réponse Hermes:" -ForegroundColor Green
    Write-Host "Content: $($response.choices[0].message.content)" -ForegroundColor White
    Write-Host "Tokens: $($response.usage.total_tokens)" -ForegroundColor Cyan
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== TERMINÉ ===" -ForegroundColor Green
