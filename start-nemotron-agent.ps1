# Script pour démarrer l'agent Nemotron avec ses propres variables
Write-Host "Démarrage de l'agent lmstudio-nemotron avec variables dédiées..."

# Variables pour Nemotron
$env:OPENAI_BASE_URL = "http://localhost:1234/v1"
if (-not $env:LM_STUDIO_API_KEY) {
    Write-Host "WARNING: LM_STUDIO_API_KEY not set. Get your key from LM Studio > Settings > Authentication." -ForegroundColor Yellow
}
$env:OPENAI_API_KEY = if ($env:LM_STUDIO_API_KEY) { $env:LM_STUDIO_API_KEY } else { "lm-studio" }
$env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"

# Arrêter et redémarrer le daemon
agn down
agn up -d

Write-Host "Agent lmstudio-nemotron configuré pour Nemotron 3 Nano sur port 1234"
Write-Host "Les autres agents restent sur Hermes-3 sur port 9000"
