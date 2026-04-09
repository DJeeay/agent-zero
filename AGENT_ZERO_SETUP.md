# Agent Zero + Llama.cpp Server Setup

## Running Configuration

Both services are now running on Docker with proper network integration:

**Start both services:**
```powershell
cd "D:\DOCKER Cont 1 AZ"
docker compose -f docker-compose.full.yml up -d
```

**Services:**
- **llama-server** (port 8080) - Hermes-3-Llama-3.1-8B local inference
- **agent-zero** (port 50080) - AI agent orchestrator

## Agent Zero Configuration

Agent Zero is configured to use your local llama-server via the `conf/model_providers.yaml` file.

### Provider Setup

Added custom provider in `model_providers.yaml`:

```yaml
llama_cpp:
  name: Llama.cpp Server (Local)
  litellm_provider: openai
  kwargs:
    api_base: http://llama-server:8080/v1
```

**To use in Agent Zero UI:**
1. Access http://localhost:50080
2. Go to Settings → Model Provider
3. Select "Llama.cpp Server (Local)"
4. Model: `Hermes-3-Llama-3.1-8B` (or auto-detected)
5. API Key: `sk-dummy` (not used but required)

## Docker Network

Both containers communicate via internal Docker bridge network (`llm-network`):
- Agent Zero → llama-server: `http://llama-server:8080/v1`
- Host → Agent Zero: `http://localhost:50080`
- Host → llama-server: `http://localhost:8080`

## Volume Mounts

**Agent Zero:**
- `/a0` → `agent0-volume` (persistent state)
- `/a0/conf` → `./conf` (read-only config)

**llama-server:**
- `/models` → `d:/llm_models` (read-only model files)

## Accessing Services

### Agent Zero Web UI
```
http://localhost:50080
```
- Chat interface
- Settings (model provider selection)
- Project management
- File uploads

### LLM Server API (Direct)
```bash
# Health check
curl http://localhost:8080/health

# Text completion
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello","n_predict":50}'

# List models (OpenAI-compatible)
curl http://localhost:8080/v1/models
```

## Files

- `docker-compose.full.yml` - Complete multi-service compose file
- `conf/model_providers.yaml` - Agent Zero model provider definitions
- `docker-compose.yml` - llama-server only (simpler)

## Troubleshooting

**Agent Zero still trying to connect to Ollama?**
- Restart Agent Zero: `docker restart agent-zero`
- Check config: `cat conf/model_providers.yaml | grep -A5 llama_cpp`

**llama-server not healthy?**
- Check logs: `docker logs llama-server --tail 30`
- Model file exists: `ls -la d:/llm_models/Hermes-3-*.gguf`
- Wait for GPU warmup (first request takes ~30sec)

**Port conflicts?**
- Verify open ports: `netstat -ano | findstr 8080` (Windows)
- Change ports in compose file and rebuild

## Next Steps

1. Open http://localhost:50080 in browser
2. Select "Llama.cpp Server (Local)" as model provider
3. Start chatting with your local LLM
4. Create projects and upload files for RAG

