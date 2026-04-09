# OpenAgents Control (OAC) - Installation pour Agent Zero + Hermes Local
param([switch]$Global = $false, [string]$InstallDir = "")
$ErrorActionPreference = "Stop"

Write-Host "Installation OpenAgents Control pour Agent Zero + Hermes-3" -ForegroundColor Cyan
Write-Host ""

# Verifier adapteur
Write-Host "Verification de l'adaptateur FastAPI..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9000/health" -Method GET -TimeoutSec 5
    if ($response.status -eq "ok") {
        Write-Host "OK - Adaptateur FastAPI accessible (port 9000)" -ForegroundColor Green
        Write-Host "   Llama server: $($response.llama_server)" -ForegroundColor Gray
    } else {
        Write-Host "ATTENTION - Adaptateur accessible mais statut: $($response.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERREUR: Adaptateur FastAPI non accessible sur http://localhost:9000" -ForegroundColor Red
    Write-Host "   Verifiez que Docker est demarre: docker-compose up -d" -ForegroundColor Red
    exit 1
}

# Creer repertoire
if ($Global) {
    $targetDir = if ($InstallDir) { $InstallDir } else { "$env:USERPROFILE\.config\opencode" }
} else {
    $targetDir = if ($InstallDir) { $InstallDir } else { ".opencode" }
}

Write-Host ""
Write-Host "Installation dans: $targetDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
New-Item -ItemType Directory -Force -Path "$targetDir\context\core" | Out-Null
New-Item -ItemType Directory -Force -Path "$targetDir\context\project-intelligence" | Out-Null
New-Item -ItemType Directory -Force -Path "$targetDir\agent\core" | Out-Null

# Config OpenCode
$config = @"
models:
  hermes-local:
    name: "Hermes-3 Local (8B Q4)"
    provider: openai
    base_url: http://localhost:9000/v1
    api_key: dummy
    model: hermes-3
    max_tokens: 2048
    temperature: 0.7

default_model: hermes-local
"@
$config | Out-File -FilePath "$targetDir\config.yaml" -Encoding UTF8
Write-Host "OK - Configuration OpenCode creee" -ForegroundColor Green

# Contexte Agent Zero
$lines = @(
    "# Agent Zero Context File pour OAC",
    "",
    "## Architecture",
    "- LLM Local: Hermes-3-Llama-3.1-8B.Q4_K_M.gguf via llama.cpp",
    "- Adaptateur FastAPI: Compatible OpenAI sur port 9000",
    "- Docker Compose: 2 services (llama-server + hermes adapter)",
    "",
    "## Endpoints",
    "- Health: http://localhost:9000/health",
    "- OpenAI API: http://localhost:9000/v1/chat/completions",
    "- Models: http://localhost:9000/v1/models",
    "- Llama direct: http://localhost:8080",
    "",
    "## Fichiers cles",
    "- adapter/adapter.py - Adaptateur FastAPI",
    "- docker-compose.yml - Configuration Docker",
    "- agent-config.json - Config type openai",
    "- .env - Variables d'environnement",
    "",
    "## Patterns",
    "- Format ChatML: <|im_start|>system, <|im_start|>user, <|im_start|>assistant",
    "- Stop tokens:  </s>",
    "- Support streaming SSE",
    "",
    "## Docker Commands",
    "- docker-compose up -d (demarrer)",
    "- docker logs -f hermes (logs adapter)",
    "- docker logs -f llama-server (logs LLM)",
    "- docker-compose restart (redemarrer)",
    "",
    "## Variables",
    "- HERMES_API_URL=http://localhost:9000/v1/chat/completions",
    "- LLAMA_URL=http://llama-server:8080",
    "- MODEL_NAME=hermes-3",
    "- LOG_LEVEL=INFO",
    "",
    "## Contraintes",
    "- Contexte max: 16384 tokens",
    "- GPU: NVIDIA CUDA avec 35 layers offload",
    "- RAM: 12GB allouee au conteneur llama-server"
)
$lines | Out-File -FilePath "$targetDir\context\project-intelligence\agent-zero.md" -Encoding UTF8
Write-Host "OK - Contexte Agent Zero cree" -ForegroundColor Green

# Agent personnalise
$agentLines = @(
    "---",
    "description: Agent specialise pour Agent Zero avec Hermes-3 local",
    "model: hermes-local",
    "---",
    "",
    "# Agent Zero Specialist",
    "",
    "Tu es un expert du framework Agent Zero avec architecture FastAPI + llama.cpp.",
    "",
    "## Expertises",
    "1. Architecture: Docker, FastAPI, llama.cpp, ChatML format",
    "2. Maintenance: adapter.py, endpoints, configuration",
    "3. Debug: Logs Docker, health checks, erreurs API",
    "4. Extension: Nouveaux endpoints, features, integrations",
    "",
    "## Contraintes Systeme",
    "- Modele: Hermes-3-Llama-3.1-8B.Q4_K_M (8B params, 4-bit quantise)",
    "- Contexte: 16384 tokens max",
    "- GPU: NVIDIA CUDA, 35 layers offload",
    "- RAM: 12GB conteneur llama-server",
    "",
    "## Patterns Critiques",
    "1. Compatibilite OpenAI: maintenir /v1/chat/completions",
    "2. Format ChatML pour Hermes-3",
    "3. Retro-compatibilite endpoint /query",
    "4. Logging approprie (INFO/DEBUG)",
    "",
    "## Fichiers Essentiels",
    "- adapter/adapter.py - Adaptateur FastAPI (300 lignes)",
    "- docker-compose.yml - 2 services Docker",
    "- agent-config.json - Config type: openai",
    "- .env - HERMES_API_URL et variables"
)
$agentLines | Out-File -FilePath "$targetDir\agent\core\agentzero-specialist.md" -Encoding UTF8
Write-Host "OK - Agent 'agentzero-specialist' cree" -ForegroundColor Green

Write-Host ""
Write-Host "Installation terminee!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor White
Write-Host "  1. Installer OpenCode CLI: https://opencode.ai/docs" -ForegroundColor Gray
Write-Host "  2. Copier config: Copy-Item '$targetDir\config.yaml' `$env:USERPROFILE\.config\opencode\" -ForegroundColor Gray
Write-Host "  3. Lancer: opencode --agent agentzero-specialist" -ForegroundColor Gray
Write-Host ""
Write-Host "Test:" -ForegroundColor White
Write-Host "  curl http://localhost:9000/v1/chat/completions -H 'Content-Type: application/json' -d '{""model"":""hermes-3"",""messages"":[{""role"":""user"",""content"":""Hello""}]}'" -ForegroundColor Gray
