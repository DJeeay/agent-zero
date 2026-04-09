# Script pour démarrer l'agent Nemotron avec ses propres variables
Write-Host "Démarrage de l'agent lmstudio-nemotron avec variables dédiées..."

# Variables pour Nemotron
$env:OPENAI_BASE_URL = "http://localhost:1234/v1"
$env:OPENAI_API_KEY = "dummy"
$env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"

# Arrêter et redémarrer le daemon
agn down
agn up -d

Write-Host "Agent lmstudio-nemotron configuré pour Nemotron 3 Nano sur port 1234"
Write-Host "Les autres agents restent sur Hermes-3 sur port 9000"
