# Agent Zero Context File pour OAC
# Ce fichier guide OAC sur l'architecture du projet

## Architecture du Projet

**Agent Zero** est un framework agentic avec:
- **LLM Local**: Hermes-3-Llama-3.1-8B.Q4_K_M.gguf via llama.cpp
- **Adaptateur FastAPI**: Compatible OpenAI sur port 9000
- **Docker Compose**: 2 services (llama-server + hermes adapter)
- **Web UI**: Interface utilisateur integree

## Endpoints Disponibles

| Endpoint | URL | Description |
|----------|-----|-------------|
| Adaptateur Health | http://localhost:9000/health | Statut de l'adaptateur |
| OpenAI Models | http://localhost:9000/v1/models | Liste des modeles |
| Chat Completions | http://localhost:9000/v1/chat/completions | API principale |
| Llama Server | http://localhost:8080 | Acces direct llama.cpp |

## Structure des Fichiers Cles

```
d:\openagents\
├── adapter\adapter.py          # Adaptateur FastAPI OpenAI-compatible (300 lignes)
├── adapter\requirements.txt    # FastAPI, uvicorn, httpx, pydantic
├── docker-compose.yml           # Configuration Docker (2 services)
├── agent-config.json            # Config Agent Zero (type: openai)
├── .env                         # Variables d'environnement
└── .opencode\                   # Configuration OAC
    ├── config.yaml              # Config OpenCode CLI
    ├── context\project-intelligence\agent-zero.md  # Ce fichier
    └── agent\core\agentzero-specialist.md          # Agent specialise
```

## Patterns de Code

### Adaptateur FastAPI
- **Format ChatML** pour Hermes-3: `<|im_start|>system`, `<|im_start|>user`, `<|im_start|>assistant`
- **Stop tokens**: `</s>`, ``
- **Support streaming SSE**: `stream=true` dans les requetes
- **Legacy endpoint** `/query` pour retro-compatibilite

### Configuration Agent Zero (agent-config.json)
```json
{
  "name": "Hermes-LLM",
  "type": "openai",
  "base_url": "http://localhost:9000/v1",
  "api_key": "dummy",
  "model": "hermes-3",
  "timeout": 120,
  "max_tokens": 512,
  "temperature": 0.7
}
```

## Commandes Docker Utiles

```powershell
# Demarrer les services
docker-compose up -d

# Voir les logs en temps reel
docker logs -f hermes
docker logs -f llama-server

# Redemarrer
docker-compose restart

# Arreter
docker-compose down

# Statut
docker ps
```

## Variables d'Environnement Cles (.env)

| Variable | Valeur | Description |
|----------|--------|-------------|
| HERMES_API_URL | http://localhost:9000/v1/chat/completions | Endpoint OpenAI |
| LLAMA_URL | http://llama-server:8080 | URL interne llama.cpp |
| MODEL_NAME | hermes-3 | Nom du modele expose |
| LOG_LEVEL | INFO | Niveau de logging |
| NOTION_API_KEY | ntn_... | Integration Notion (optionnel) |

## Contraintes Systeme

- **Modele**: Hermes-3-Llama-3.1-8B.Q4_K_M (8B parametres, 4-bit quantise)
- **Contexte max**: 16384 tokens
- **GPU**: NVIDIA avec CUDA (35 layers offload via `--n-gpu-layers 35`)
- **RAM**: 12GB allouee au conteneur llama-server
- **Timeout adaptateur**: 120 secondes

## Tests Rapides

```bash
# Health check
curl http://localhost:9000/health

# Liste modeles
curl http://localhost:9000/v1/models

# Chat completion simple
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes-3","messages":[{"role":"user","content":"Hello"}]}'

# Chat avec system prompt
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model":"hermes-3",
    "messages":[
      {"role":"system","content":"Tu es un assistant utile."},
      {"role":"user","content":"Quelle est la capitale de la France?"}
    ],
    "max_tokens":100
  }'
```

## Integration avec OAC

Cette configuration permet a OAC d'utiliser le LLM local Hermes-3 via l'adaptateur FastAPI.

**Avantages**:
- Gratuit (pas de couts API)
- Prive (donnees restent locales)
- Rapide (execution GPU local)
- Compatible OpenAI (fonctionne avec OAC, LangChain, etc.)

## Depannage Courant

| Probleme | Solution |
|----------|----------|
| "llama.cpp unreachable" | Verifier `docker ps`, redemarrer les conteneurs |
| Reponses vides | Verifier format ChatML, augmenter max_tokens |
| Timeout | Augmenter timeout dans agent-config.json |
| CORS errors | Deja gere par l'adaptateur (middleware CORS actif) |
