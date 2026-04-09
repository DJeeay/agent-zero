# Switch between agent configurations
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("hermes", "nemotron")]
    [string]$Agent
)

Write-Host "Switching to $Agent configuration..."

if ($Agent -eq "hermes") {
    $env:OPENAI_BASE_URL = "http://localhost:9000/v1"
    $env:OPENAI_API_KEY = "dummy"
    $env:NANOCLAW_MODEL = "hermes-3"
    Write-Host "Hermes agents configured (port 9000)"
}
elseif ($Agent -eq "nemotron") {
    $env:OPENAI_BASE_URL = "http://localhost:1234/v1"
    $env:OPENAI_API_KEY = "dummy"
    $env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"
    Write-Host "Nemotron agent configured (port 1234)"
}

# Restart daemon
agn down
agn up -d

Write-Host "Ready to test $Agent agents!"
