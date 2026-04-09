# Docker Agent Setup - COMPLETE GUIDE
# For Présence-Parcours Automation

## ✅ WHAT WAS SET UP

You now have a unified Docker Agent system with:

1. **LLM Server** (llm-server-presparc)
   - Hermes 3.1-8B model running locally
   - GPU accelerated via CUDA
   - Health checks enabled
   - Port: 8080

2. **Docker Agent** (presparc-agent)
   - Orchestrator for all automation
   - Configured in cagent.yaml
   - Port: 8000 (API endpoint)
   - Replaces Agent Zero, Hermes Agent, and manual Notion integration

3. **Configuration**
   - cagent.yaml: Your agent definition
   - .env: Environment variables
   - agent_memory/: Agent learning memory
   - logs/: Operational logs

---

## 🚀 QUICK START

### Start Everything
```bash
docker compose -f docker-compose-agent-simple.yml up -d
```

### View Status
```bash
docker compose -f docker-compose-agent-simple.yml ps
docker compose -f docker-compose-agent-simple.yml logs -f presparc-agent
```

### Stop Everything
```bash
docker compose -f docker-compose-agent-simple.yml down
```

---

## 📋 NEXT STEPS

### Step 1: Get Your Notion API Key (5 minutes)
1. Go to: https://www.notion.so/my-integrations
2. Click "Create new integration"
3. Name it: "Presparc Agent"
4. Copy the API Key
5. Edit .env and paste it:
   ```
   NOTION_API_KEY=secret_xxxxxxxxxxxxx
   ```

### Step 2: Get Your Database ID (2 minutes)
1. Open your Notion database
2. Look at the URL: 
   ```
   https://notion.so/xxxxx?v=xxxxx
   ```
3. Copy the long ID before the `?`
4. Edit .env:
   ```
   NOTION_DATABASE_ID=xxxxx
   ```

### Step 3: Restart Agent with Keys
```bash
docker compose -f docker-compose-agent-simple.yml restart presparc-agent
```

### Step 4: Interact with Your Agent
```bash
docker compose -f docker-compose-agent-simple.yml exec presparc-agent cagent interact
```

Then ask:
- "Sync all students from my Notion database"
- "Create a lesson plan for tomorrow"
- "Analyze student progress this week"
- "Generate parent communications"

---

## 🎯 WHAT THE AGENT CAN DO

With cagent.yaml configured, your agent can:

### Student Management
- ✅ Pull student data from Notion
- ✅ Track progress automatically
- ✅ Flag at-risk students
- ✅ Suggest interventions

### Lesson Planning
- ✅ Create lessons based on student level
- ✅ Align with pedagogical standards
- ✅ Track learning objectives
- ✅ Generate materials

### Parent Communication
- ✅ Write weekly progress reports
- ✅ Highlight achievements
- ✅ Suggest home activities
- ✅ Respond to concerns

### Automation
- ✅ Daily sync from Notion (6 AM)
- ✅ Weekly report generation (Monday 9 AM)
- ✅ Monthly deep analysis (1st of month, 3 AM)
- ✅ Lesson planning (Friday 10 AM)

---

## 🔧 TROUBLESHOOTING

### LLM Server not starting?
```bash
docker logs llm-server-presparc
# Look for CUDA errors or model file issues
# Model path: d:/llm_models/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
```

### Agent not responding?
```bash
docker logs presparc-agent
# Check for LLM connection issues
# Check for Notion API key errors (if configured)
```

### Health check failing?
```bash
docker inspect llm-server-presparc --format='{{json .State.Health}}' | ConvertFrom-Json
# Normal during startup (30-60 seconds)
```

### Memory issues?
```bash
docker stats llm-server-presparc presparc-agent
# LLM should use ~8-12GB
# Agent should use <2GB
```

---

## 📊 MONITORING

### View real-time status
```bash
docker stats llm-server-presparc presparc-agent --no-stream
```

### View agent logs
```bash
docker compose -f docker-compose-agent-simple.yml logs -f presparc-agent
```

### View agent memory (learned information)
```bash
ls -la agent_memory/
```

### View operation logs
```bash
ls -la logs/
```

---

## 🔐 ENVIRONMENT VARIABLES

Required (for Notion):
- NOTION_API_KEY: Your Notion integration token
- NOTION_DATABASE_ID: Your database ID

Optional (fallback LLMs):
- OPENAI_API_KEY: For GPT-4 fallback
- ANTHROPIC_API_KEY: For Claude fallback

See .env for all options.

---

## 📚 LEARNING MORE

- Docker Agent docs: https://docs.docker.com/ai/docker-agent/
- cagent YAML format: https://docs.docker.com/ai/cagent/
- MCP tools (300+): https://www.docker.com/products/mcp-catalog-and-toolkit/

---

## ❓ COMMON QUESTIONS

**Q: Why Docker Agent instead of Agent Zero?**
A: Docker Agent is local-first, simpler, more reliable, and better integrated with Docker.

**Q: Can I run multiple agents?**
A: Yes! Create separate cagent.yaml files and run multiple containers.

**Q: What if Notion API fails?**
A: Agent falls back to local operation, file-based tasks still work.

**Q: How do I add custom tools?**
A: Use MCP integration or write Python directly in cagent.yaml.

**Q: Can I run this in production?**
A: Yes. Recommended setup: Docker Compose on single host, Docker Swarm for HA.

---

## 📞 NEXT ACTIONS

1. ✅ Docker Agent setup complete
2. ⏭️ Get Notion API key (5 min)
3. ⏭️ Configure .env (2 min)
4. ⏭️ Restart agent (30 sec)
5. ⏭️ Start using! (unlimited)

---

**You're all set! Your Docker Agent is ready.**

Questions? Check the logs:
```bash
docker compose -f docker-compose-agent-simple.yml logs -f presparc-agent
```
