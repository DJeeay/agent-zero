# OpenAgents LM Studio Integration - Complete Project Handout

## 📋 Project Overview

**Project Name**: OpenAgents LM Studio Integration  
**Objective**: Integrate NVIDIA Nemotron 3 Nano 4B (via LM Studio) and Hermes-3 models into OpenAgents framework  
**Date**: April 9-10, 2026  
**Status**: Partially Complete (3/5 agents functional)

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenAgents Framework                      │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  hermes-local   │  │ cagent-hermes   │  (BROKEN)        │
│  │  (nanoclaw)     │  │  (nanoclaw)     │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                           │
│           └────────────────────┘                           │
│                      │                                      │
│           ┌──────────▼──────────┐                          │
│           │  Hermes FastAPI       │                          │
│           │  Adapter (Port 9000)  │  (JSON ERROR)           │
│           └──────────┬────────────┘                          │
│                      │                                      │
│           ┌──────────▼──────────┐                          │
│           │  llama.cpp Server     │                          │
│           │  (Port 8080)          │                          │
│           └───────────────────────┘                          │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  openclaw-wcot  │  │  openclaw-dzna  │  (WORKING)       │
│  │  (native)       │  │  (native)       │                  │
│  └─────────────────┘  └─────────────────┘                  │
│                                                              │
│  ┌─────────────────────────────────────┐                    │
│  │     lmstudio-nemotron               │  (FIXED)         │
│  │     (nanoclaw)                      │                  │
│  └──────────────┬──────────────────────┘                    │
│                 │                                            │
│     ┌───────────▼───────────┐                                │
│     │   LM Studio API     │                                │
│     │   (Port 1234)       │                                │
│     └─────────────────────┘                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration Files

### 1. Main Configuration: `daemon.yaml`

**Location**: `C:\Users\DJE\.openagents\daemon.yaml`

**Current State** (with issues):
```yaml
version: 2
agents:
- name: hermes-local
  type: nanoclaw
  role: worker
  OPENAI_BASE_URL: http://localhost:9000/v1
  OPENAI_API_KEY: lm-studio
  NANOCLAW_MODEL: hermes-3
  network: 0deff101
  
- name: cagent-hermes
  type: nanoclaw
  role: worker
  OPENAI_BASE_URL: http://localhost:9000/v1
  OPENAI_API_KEY: lm-studio
  NANOCLAW_MODEL: hermes-3
  network: 0deff101
  
- name: lmstudio-nemotron
  type: nanoclaw
  role: worker
  OPENAI_BASE_URL: http://localhost:1234  # ⚠️ MISSING /v1
  OPENAI_API_KEY: lm-studio
  NANOCLAW_MODEL: nvidia-nemotron-3-nano-4b
  network: 282e567e-3312-4a77-8287-5f4d3ea4b6da  # ⚠️ WRONG: should be 0deff101

networks:
- id: 282e567e-3312-4a77-8287-5f4d3ea4b6da
  slug: 0deff101
  name: Sceaux-Piquets
  endpoint: "https://workspace-endpoint.openagents.org"
  token: iMVeZQYjUrRq10FotiQnQiwOOFbcb-U9qnzLOtHhxJ8
```

**Issues in Current Config**:
1. ❌ `lmstudio-nemotron`: `OPENAI_BASE_URL` missing `/v1` suffix
2. ❌ `lmstudio-nemotron`: Network should be `0deff101` (slug), not the full ID
3. ⚠️ API keys changed from `dummy` to `lm-studio` (may work but inconsistent)

**Recommended Fixed Config**:
```yaml
version: 2
agents:
- name: hermes-local
  type: nanoclaw
  role: worker
  env:
    OPENAI_BASE_URL: http://localhost:9000/v1
    OPENAI_API_KEY: dummy
    NANOCLAW_MODEL: hermes-3
  network: 0deff101
  
- name: cagent-hermes
  type: nanoclaw
  role: worker
  env:
    OPENAI_BASE_URL: http://localhost:9000/v1
    OPENAI_API_KEY: dummy
    NANOCLAW_MODEL: hermes-3
  network: 0deff101
  
- name: lmstudio-nemotron
  type: nanoclaw
  role: worker
  env:
    OPENAI_BASE_URL: http://localhost:1234/v1  # ✅ FIXED: added /v1
    OPENAI_API_KEY: dummy
    NANOCLAW_MODEL: nvidia-nemotron-3-nano-4b
  network: 0deff101  # ✅ FIXED: use slug, not full ID

networks:
- id: 282e567e-3312-4a77-8287-5f4d3ea4b6da
  slug: 0deff101
  name: Sceaux-Piquets
  endpoint: "https://workspace-endpoint.openagents.org"
  token: iMVeZQYjUrRq10FotiQnQiwOOFbcb-U9qnzLOtHhxJ8
```

---

### 2. Docker Compose: `docker-compose.yml`

**Location**: `d:\openagents\docker-compose.yml`

```yaml
version: "3.8"

services:
  llama-server:
    image: ghcr.io/ggml-org/llama.cpp:full-cuda
    container_name: llama-server
    ports:
      - "8080:8080"
    volumes:
      - ./models:/models
    command: >
      --server --model /models/hermes-3-llama-3.1-8b.Q4_K_M.gguf
      --host 0.0.0.0 --port 8080
      --n-gpu-layers 35
      --flash-attn
      --ctx-size 8192
      --batch-size 512
      --cache-prompt
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - agent-network

  hermes:
    build:
      context: ./adapter
      dockerfile: Dockerfile
    container_name: hermes
    ports:
      - "9000:9000"
    environment:
      - LLAMA_BASE_URL=http://llama-server:8080
    depends_on:
      llama-server:
        condition: service_healthy
    networks:
      - agent-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

networks:
  agent-network:
    driver: bridge
```

---

### 3. FastAPI Adapter

**Location**: `d:\openagents\adapter\adapter.py`

**Purpose**: OpenAI-compatible API adapter for llama.cpp

**Key Features**:
- Converts OpenAI chat format to llama.cpp completion format
- Handles streaming responses
- Health check endpoint
- JSON error handling

**Known Issue**: Returns JSON parsing error (`parse error at line 1, column 1`) - needs debugging

---

## 📊 Agent Status Summary

| Agent | Type | Status | Endpoint | Issue |
|-------|------|--------|----------|-------|
| **hermes-local** | nanoclaw | 🔴 BROKEN | Port 9000 | JSON parsing error |
| **cagent-hermes** | nanoclaw | 🔴 BROKEN | Port 9000 | JSON parsing error |
| **lmstudio-nemotron** | nanoclaw | 🟡 NEEDS FIX | Port 1234 | Config issues (missing /v1, wrong network) |
| **openclaw-wcot** | openclaw | 🟢 WORKING | Built-in | Fully functional |
| **openclaw-dzna** | openclaw | 🟢 WORKING | Built-in | Fully functional |

---

## 🔧 Fixes Applied

### 1. LM Studio Nemotron Fix (April 9, 2026)

**Problem**: `read ECONNRESET` error

**Root Cause**: Incorrect environment variables in daemon.yaml

**Solution Applied**:
```powershell
# Set correct environment variables
$env:OPENAI_BASE_URL = "http://localhost:1234/v1"
$env:OPENAI_API_KEY = "dummy"
$env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"

# Restart daemon
agn down
agn up -d
```

**Result**: ✅ Nemotron started responding correctly

---

## 📁 Scripts Created

### 1. `switch-agent.ps1`
Switches between Hermes and Nemotron configurations by setting environment variables

### 2. `performance-test.ps1` & `performance-test-fixed.ps1`
Performance testing scripts for measuring response times and tokens/second

### 3. `nemotron-fix.ps1`
Automated fix for Nemotron ECONNRESET error

### 4. `hermes-fix.ps1`
Attempted fix for Hermes JSON error (not fully resolved)

### 5. `final-test.ps1`
Comprehensive test of all agents

### 6. `final-solution.ps1`
Summary of working vs broken agents with usage recommendations

---

## 🔍 Performance Analysis (Completed)

### Response Time Comparison

| Model | Avg Response | Fastest | Slowest |
|-------|-------------|---------|---------|
| Hermes-3 | 1,734 ms | 565 ms | 2,946 ms |
| Nemotron-3-Nano | 3,273 ms | 691 ms | 5,539 ms |

### Tokens/Second
- **Nemotron**: ~40 tokens/sec (when working)
- **Hermes**: Unable to measure (JSON error)

### Bottlenecks Identified
1. **Token counting bug** in Hermes adapter (returns -1)
2. **High latency variance** (565ms - 5,539ms)
3. **Model loading time** for llama.cpp

---

## 📚 Documentation Created

1. **README-AGENTS.md** - Agent configuration guide
2. **PERFORMANCE-REPORT.md** - Detailed performance analysis
3. **PROJECT-HANDOUT.md** - This document

---

## 🚀 Immediate Action Items

### High Priority (Fix Now)

1. **Fix daemon.yaml for Nemotron**:
   ```yaml
   # Change this:
   OPENAI_BASE_URL: http://localhost:1234
   network: 282e567e-3312-4a77-8287-5f4d3ea4b6da
   
   # To this:
   OPENAI_BASE_URL: http://localhost:1234/v1
   network: 0deff101
   ```

2. **Restart daemon**:
   ```bash
   agn down
   agn up -d
   ```

### Medium Priority

3. **Fix Hermes adapter JSON error**:
   - Debug adapter.py parsing error
   - Or switch to direct llama.cpp API

4. **Verify LM Studio is running**:
   - Open LM Studio
   - Load Nemotron model
   - Click "Start Server"

### Low Priority

5. **Optimize performance**:
   - Tune GPU layers
   - Adjust batch sizes
   - Enable KV cache

---

## 🎯 Usage Recommendations

### Immediate Use (Working Now)

**Use these agents for chat**:
1. `openclaw-wcot` - Native agent, fully functional
2. `openclaw-dzna` - Native agent, fully functional

**Use with caution**:
3. `lmstudio-nemotron` - After fixing config issues (see Action Items)

### Avoid Until Fixed

- ❌ `hermes-local` - JSON parsing error
- ❌ `cagent-hermes` - JSON parsing error

---

## 📝 Command Reference

### Daemon Control
```bash
# Start daemon
agn up -d

# Stop daemon
agn down

# Check status
agn status

# View logs
agn logs --tail 50

# Agent-specific logs
agn logs --agent hermes-local --tail 20
```

### Docker Control
```bash
# Start services
docker-compose up -d

# Restart hermes adapter
docker restart hermes

# Check container logs
docker logs hermes --tail 20
docker logs llama-server --tail 20
```

### API Testing
```bash
# Test Hermes adapter
curl -s http://localhost:9000/health

# Test Nemotron (LM Studio)
curl -s http://localhost:1234/v1/models

# Send chat request
curl -s -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia-nemotron-3-nano-4b","messages":[{"role":"user","content":"Hello"}]}'
```

---

## 🔮 Next Steps

1. **Fix daemon.yaml** network and URL issues
2. **Debug Hermes adapter** JSON parsing error
3. **Verify all agents** respond correctly in OpenAgents Web UI
4. **Optimize performance** based on performance report recommendations
5. **Document** final working configuration

---

## 📞 Support

For issues:
1. Check daemon logs: `agn logs --tail 50`
2. Verify LM Studio is running with "Start Server"
3. Test API endpoints directly with curl
4. Check docker container status: `docker ps`

---

**Project Status**: 🟡 Partially Functional  
**Last Updated**: April 10, 2026  
**Next Review**: After fixing daemon.yaml issues
