# Agent Zero + LLM Server Integration Guide

## Current Setup

### Running Services
- **llama-server** (Port 8080)
  - Image: `ghcr.io/ggml-org/llama.cpp:full-cuda`
  - Model: `Hermes-3-Llama-3.1-8B.Q4_K_M.gguf`
  - Context Window: 16384 tokens
  - GPU Layers: 20
  - Memory Limit: 12GB
  - Status: Starting (model loading)

### Network
- **Network**: `llm-network` (bridge)
- **Container IPs**: llama-server at 172.20.0.2

## Connecting Agent Zero to LLM Server

### Option 1: Start Both Together (Recommended)

```powershell
cd "D:\DOCKER Cont 1 AZ"
docker compose -f docker-compose.agent-zero.yml up -d
```

This uses `docker-compose.agent-zero.yml` which includes both services on the same network.

**Access Points:**
- Agent Zero: http://localhost:50080
- LLM Server: http://localhost:8080

### Option 2: Start Agent Zero with Existing llama-server

```powershell
docker run -d `
  --name agent-zero `
  --restart unless-stopped `
  -p 50080:80 `
  -v agent0-volume:/a0 `
  --network llm-network `
  -e LLM_API_URL="http://llama-server:8080" `
  -e LLM_API_TYPE="openai-compatible" `
  -e LLM_MODEL="Hermes-3-Llama-3.1-8B" `
  -e AGENT_LOG_LEVEL="INFO" `
  agent0ai/agent-zero:latest
```

## Verifying Communication

### 1. Check llama-server Health
```powershell
docker logs llama-server --tail 20
docker ps --filter "name=llama-server"
```

Wait for status to change from `unhealthy` to `healthy` (~2-5 minutes during model loading).

### 2. Test LLM API Directly
```powershell
# Once healthy, test the API
$body = @{prompt="Hello, world!"; temperature=0.7} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8080/completion" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### 3. Check Agent Zero Logs (if running)
```powershell
docker logs agent-zero -f
```

Look for successful API calls to llama-server.

## Environment Variables for Agent Zero

The compose file passes these to Agent Zero:

```yaml
environment:
  LLM_API_URL: "http://llama-server:8080"     # Internal Docker network URL
  LLM_API_TYPE: "openai-compatible"            # API protocol
  LLM_MODEL: "Hermes-3-Llama-3.1-8B"          # Model name (for identification)
  AGENT_LOG_LEVEL: "INFO"                     # Logging level
```

## Troubleshooting

### llama-server takes too long to load
- First startup can take 5-10 minutes while GGML loads tensors to GPU
- Check logs: `docker logs llama-server --tail 50 -f`
- Wait for: "ready = true"

### Agent Zero can't reach llama-server
- Verify network: `docker network inspect llm-network`
- Check llama-server IP and port: `docker inspect llama-server | findstr -i "ipaddr\|port"`
- Ensure both containers are on same network

### API returns 503 Service Unavailable
- Model still loading
- Wait for health check to show "healthy"
- Agent Zero will automatically retry

### Out of Memory (OOM) errors
- llama-server has 12GB hard limit
- Reduce context size or GPU layers in docker-compose.yml
- Reduce batch size

## Files Generated

1. **docker-compose.yml** - LLM server only (current setup)
2. **docker-compose.agent-zero.yml** - Both services together
3. **verify-setup.ps1** - Health and connectivity test script

## Next Steps

1. **Wait for llama-server to be healthy**
   ```powershell
   docker ps
   # Should show: "Up X minutes (healthy)"
   ```

2. **Test LLM API**
   ```powershell
   ./verify-setup.ps1
   ```

3. **Start Agent Zero**
   ```powershell
   docker compose -f docker-compose.agent-zero.yml up -d
   ```

4. **Access and Test**
   - Agent Zero UI: http://localhost:50080
   - Check logs: `docker logs agent-zero -f`

## API Documentation

### LLM Server Endpoints

#### Health Check
```
GET http://localhost:8080/health
Response: {"status":"ok"} (when healthy)
```

#### Completion (Text Generation)
```
POST http://localhost:8080/completion
Content-Type: application/json

{
  "prompt": "Your text here",
  "temperature": 0.7,
  "top_p": 0.9,
  "n_predict": 128
}
```

#### Models (OpenAI-compatible)
```
GET http://localhost:8080/v1/models
Response: {"object":"list","data":[{"id":"Hermes-3-Llama-3.1-8B","object":"model"}]}
```

## Performance Tuning

If you have multiple GPUs:

```yaml
# Use GPU 0 for llama-server, GPU 1 for other services
environment:
  CUDA_VISIBLE_DEVICES: "0"
```

Reduce context if memory issues:
```yaml
command: >
  --server
  -m /models/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
  --ctx-size 8192  # Reduced from 16384
  -ngl 20
```

Increase throughput with larger batch size:
```yaml
command: >
  --server
  -m /models/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
  --batch-size 1024
```

## References

- llama.cpp docs: https://github.com/ggerganov/llama.cpp
- Agent Zero docs: https://github.com/agentzero-ai/agent-zero
- Docker Compose: https://docs.docker.com/compose/
