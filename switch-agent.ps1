# Switch between agent configurations
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("hermes", "nemotron")]
    [string]$Agent
)

Write-Host "Switching to $Agent configuration..."

if ($Agent -eq "hermes") {
    $env:OPENAI_BASE_URL = "http://localhost:9000/v1"
    if (-not $env:OPENAI_API_KEY) { $env:OPENAI_API_KEY = "lm-studio" }
    $env:NANOCLAW_MODEL = "hermes-3"
    Write-Host "Hermes agents configured (port 9000)"
}
elseif ($Agent -eq "nemotron") {
    $env:OPENAI_BASE_URL = "http://localhost:1234/v1"
    if (-not $env:LM_STUDIO_API_KEY) {
        Write-Host "WARNING: LM_STUDIO_API_KEY not set. Set it from LM Studio > Settings > Authentication." -ForegroundColor Yellow
    }
    $env:OPENAI_API_KEY = if ($env:LM_STUDIO_API_KEY) { $env:LM_STUDIO_API_KEY } else { "lm-studio" }
    $env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"
    Write-Host "Nemotron agent configured (port 1234)"
}

# Restart daemon
agn down
agn up -d

Write-Host "Ready to test $Agent agents!"
