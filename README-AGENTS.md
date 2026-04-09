# OpenAgents - Configuration des Agents

## Agents Disponibles

| Agent | Type | Backend | Port | Modèle | Statut |
|-------|------|---------|------|--------|--------|
| hermes-local | nanoclaw | Docker FastAPI | 9000 | hermes-3 | **Fonctionnel** |
| cagent-hermes | nanoclaw | Docker FastAPI | 9000 | hermes-3 | **Fonctionnel** |
| openclaw-wcot | openclaw | Built-in natif | - | - | **Fonctionnel** |
| openclaw-dzna | openclaw | Built-in natif | - | - | **Fonctionnel** |
| lmstudio-nemotron | nanoclaw | LM Studio | 1234 | nvidia-nemotron-3-nano-4b | **Fonctionnel** |

## Commandes

### Démarrer les agents Hermes
```powershell
./switch-agent.ps1 -Agent hermes
```

### Démarrer l'agent Nemotron
```powershell
./switch-agent.ps1 -Agent nemotron
```

### Vérifier le statut
```powershell
agn status
```

### Voir les logs
```powershell
agn logs --tail 20
```

## Architecture

### Hermes (Docker)
- **llama-server**: Port 8080 (llama.cpp + Hermes-3)
- **hermes**: Port 9000 (FastAPI adapter OpenAI-compatible)

### LM Studio
- **Server**: Port 1234 (API OpenAI-compatible)
- **Modèle**: NVIDIA Nemotron 3 Nano 4B

## Tests API

### Test Hermes
```powershell
Invoke-RestMethod -Uri "http://localhost:9000/v1/chat/completions" -Method POST -ContentType "application/json" -Body '{"model":"hermes-3","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

### Test Nemotron
```powershell
Invoke-RestMethod -Uri "http://localhost:1234/v1/chat/completions" -Method POST -ContentType "application/json" -Body '{"model":"nvidia-nemotron-3-nano-4b","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'
```

## Résolution des Problèmes

### Erreur "Unknown agent type: custom"
- Corrigé: Utiliser `nanoclaw` au lieu de `custom`

### Fenêtres CMD popup
- Corrigé: Utiliser `nanoclaw` (adapter natif) au lieu de `opencode`

### Variables d'environnement
- Les agents `nanoclaw` partagent les variables globales
- Utiliser `switch-agent.ps1` pour basculer entre configurations
