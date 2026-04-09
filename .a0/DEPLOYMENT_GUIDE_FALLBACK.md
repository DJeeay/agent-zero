# 🚀 GUIDE IMPLÉMENTATION: FALLBACK MULTI-PROVIDER

## Phase 1: DEPLOYMENT (2-3 heures)

### Étape 1.1: Vérifier Ressources GPU (10 min)

```bash
# Vérifier VRAM disponible
nvidia-smi

# Résultat attendu:
# GPU 0: 24GB total (min requis pour 3 modèles = 11GB)
# Si <12GB: Réduire à 2 modèles (primary + fallback1 seulement)
```

### Étape 1.2: Lancer Fallback1 - Hermes-3.2-3B (30 min)

```bash
docker run -d \
  --gpus=all \
  -v "d:/llm_models:/models:ro" \
  -p 8081:8080 \
  --name hermes-3b-light \
  --restart unless-stopped \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  /app/tools.sh --server \
  -m /models/Hermes-3-Llama-3.2-3B-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 4096 \
  --n-gpu-layers 20 \
  --threads 8
```

**Vérifier démarrage:**
```bash
docker logs hermes-3b-light | tail -20
# Chercher: "main: server is listening on http://0.0.0.0:8080"

# Test santé
curl http://localhost:8081/health
# Résultat attendu: {"status":"ok"}
```

### Étape 1.3: Lancer Fallback2 - Qwen-7B (30 min)

```bash
docker run -d \
  --gpus=all \
  -v "d:/llm_models:/models:ro" \
  -p 8082:8080 \
  --name qwen-7b \
  --restart unless-stopped \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  /app/tools.sh --server \
  -m /models/Qwen2.5-7b-instruct-q4_k_m.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 8192 \
  --n-gpu-layers 20 \
  --threads 8
```

**Vérifier démarrage:**
```bash
docker logs qwen-7b | tail -20

# Test santé
curl http://localhost:8082/health
```

### Étape 1.4: Tester les 3 endpoints

```bash
# Provider 1
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes","messages":[{"role":"user","content":"hi"}],"stream":false}' \
  | jq '.choices[0].message.content'

# Provider 2
curl -X POST http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"hermes","messages":[{"role":"user","content":"hi"}],"stream":false}' \
  | jq '.choices[0].message.content'

# Provider 3
curl -X POST http://localhost:8082/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen","messages":[{"role":"user","content":"hi"}],"stream":false}' \
  | jq '.choices[0].message.content'
```

**Résultat attendu:** 3 réponses différentes (3 modèles différents)

---

## Phase 2: CONFIGURATION AGENT ZERO (30 min)

### Étape 2.1: Sauvegarder Config Actuelle

```bash
# Backup
cp ~/.a0/config.yaml ~/.a0/config.yaml.backup.single_provider
```

### Étape 2.2: Activer Config Multi-Provider

**Option A: Remplacer complètement**
```bash
cp ~/.a0/config_multi_provider.yaml ~/.a0/config.yaml
```

**Option B: Merge manuellement**
```bash
# Ajouter sections "multi_provider" et "fallback_settings"
# À partir du fichier config_multi_provider.yaml
# Dans le config.yaml existant
```

### Étape 2.3: Vérifier Config

```bash
# Vérifier syntaxe YAML
python3 -c "import yaml; yaml.safe_load(open('~/.a0/config.yaml'))" && echo "✅ YAML valid"

# Vérifier endpoints accessibles
for port in 8080 8081 8082; do
  curl -s http://localhost:$port/health | jq '.' && echo "✅ Port $port OK" || echo "❌ Port $port FAIL"
done
```

---

## Phase 3: TEST FALLBACK (30 min)

### Test 3.1: Kill Primary, Verify Fallback

**Terminal 1: Monitorer logs Agent Zero**
```bash
tail -f ~/.a0/logs/agent_zero.log | grep -E "fallback|provider|error"
```

**Terminal 2: Kill primary**
```bash
docker stop llama-server
```

**Terminal 3: Test Agent Zero**
```bash
# Tester extension qui utilise LLM
curl http://localhost:50080/api/agent/memorize_solutions \
  -d '{"content":"Important info"}' \
  -H "Content-Type: application/json"

# Résultat attendu:
# - Logs montrent "Primary provider down"
# - Logs montrent "Fallback1 (port 8081) trying..."
# - Request réussit (avec latence accrue)
```

### Test 3.2: Kill Fallback1, Verify Fallback2

**Terminal 1: Monitorer logs**
```bash
tail -f ~/.a0/logs/agent_zero.log | grep -E "fallback"
```

**Terminal 2: Kill fallback1**
```bash
docker stop hermes-3b-light
```

**Terminal 3: Test Agent Zero**
```bash
# Request devrait utiliser fallback2 (Qwen-7B)
curl http://localhost:50080/api/agent/memorize_solutions \
  -d '{"content":"Another test"}' \
  -H "Content-Type: application/json"

# Résultat attendu:
# - Logs montrent "Fallback1 provider down"
# - Logs montrent "Fallback2 (port 8082) trying..."
# - Request réussit (avec latence accrue)
```

### Test 3.3: Auto-Recovery

**Terminal 1: Monitorer logs**
```bash
tail -f ~/.a0/logs/agent_zero.log | grep -E "recovered|primary|restored"
```

**Terminal 2: Redémarrer tous les containers**
```bash
docker start llama-server hermes-3b-light
```

**Terminal 3: Test Agent Zero**
```bash
# Request devrait revenir à Primary
curl http://localhost:50080/api/agent/memorize_solutions \
  -d '{"content":"Recovery test"}' \
  -H "Content-Type: application/json"

# Résultat attendu:
# - Logs montrent "Primary provider recovered"
# - Logs montrent "Switching back to primary"
# - Latence revient à 50ms normal
```

---

## Phase 4: MONITORING (15 min)

### Créer Dashboard Monitoring

```bash
cat > ~/.a0/monitor_fallback.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "=== MULTI-PROVIDER HEALTH ==="
  echo "Time: $(date)"
  echo ""
  
  for port in 8080 8081 8082; do
    name=""
    case $port in
      8080) name="Primary (Hermes-3-8B)" ;;
      8081) name="Fallback1 (Hermes-3.2-3B)" ;;
      8082) name="Fallback2 (Qwen-7B)" ;;
    esac
    
    if curl -s -m 2 http://localhost:$port/health > /dev/null 2>&1; then
      echo "✅ $name (port $port): HEALTHY"
    else
      echo "❌ $name (port $port): DOWN"
    fi
  done
  
  echo ""
  echo "=== RECENT FALLBACK EVENTS ==="
  tail -5 ~/.a0/logs/agent_zero.log | grep -i fallback
  
  echo ""
  echo "=== RESOURCE USAGE ==="
  docker stats llama-server hermes-3b-light qwen-7b --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.CPUPerc}}"
  
  sleep 10
done
EOF

chmod +x ~/.a0/monitor_fallback.sh
~/.a0/monitor_fallback.sh
```

### Alerting (Optionnel)

```bash
cat > ~/.a0/fallback_alerts.py << 'EOF'
#!/usr/bin/env python3
import requests
import time
import logging

PROVIDERS = [
    {"port": 8080, "name": "Primary", "timeout": 5},
    {"port": 8081, "name": "Fallback1", "timeout": 8},
    {"port": 8082, "name": "Fallback2", "timeout": 10},
]

logging.basicConfig(filename='~/.a0/logs/fallback_alerts.log')

def check_provider(port, timeout):
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    failed_providers = []
    
    for provider in PROVIDERS:
        is_healthy = check_provider(provider["port"], provider["timeout"])
        if not is_healthy:
            failed_providers.append(provider)
            logging.error(f"Provider {provider['name']} DOWN")
    
    if len(failed_providers) >= 2:
        logging.critical(f"ALERT: Only {3 - len(failed_providers)} provider(s) available!")
    
    if len(failed_providers) == 3:
        logging.critical(f"ALERT: ALL PROVIDERS DOWN! System unavailable!")

if __name__ == '__main__':
    while True:
        main()
        time.sleep(30)  # Check every 30 seconds
EOF

chmod +x ~/.a0/fallback_alerts.py
python3 ~/.a0/fallback_alerts.py &
```

---

## Phase 5: VERIFICATION FINALE (15 min)

### Checklist

- [ ] Tous 3 containers démarrent sans erreur
- [ ] Tous 3 endpoints répondent à /health
- [ ] Agent Zero config valide (YAML syntax OK)
- [ ] Primary kill → Fallback1 utilisé ✅
- [ ] Fallback1 kill → Fallback2 utilisé ✅
- [ ] Restart primary → Auto-switch back ✅
- [ ] Logs montrent fallback events
- [ ] Pas de requêtes perdues pendant fallback
- [ ] Latence acceptable même en fallback2 (<2s)

### Performance Baseline

Avant activation fallback (à conserver pour comparaison):
```
Primary only:
  - Average latency: _____ ms
  - Max latency: _____ ms
  - Uptime: _____ %
  - Errors: _____ /day
```

Après activation fallback (à mesurer après 1 semaine):
```
With fallback:
  - Average latency: _____ ms
  - Max latency: _____ ms
  - Uptime: _____ %
  - Errors: _____ /day
  - Fallback events: _____ /day
```

---

## ROLLBACK PLAN (if issues)

Si problèmes rencontrés:

```bash
# 1. Restore config single-provider
cp ~/.a0/config.yaml.backup.single_provider ~/.a0/config.yaml

# 2. Redémarrer Agent Zero
docker restart agent-zero

# 3. Kill fallback containers (optional)
docker stop hermes-3b-light qwen-7b
docker rm hermes-3b-light qwen-7b

# 4. System revient à state initial
```

---

## SUPPORT & TROUBLESHOOTING

### Symptom: "Fallback never triggered even when primary down"
**Cause:** Health check désactivé ou config pas rechargée
**Fix:** Redémarrer agent-zero, vérifier logs pour config load errors

### Symptom: "VRAM exhausted, models crashing"
**Cause:** 3 modèles trop lourds pour GPU
**Fix:** Réduire à 2 modèles (primary + fallback1), réduire n-gpu-layers

### Symptom: "Latency très élevée même avec fallback"
**Cause:** Tous providers overloaded
**Fix:** Réduire max_concurrent_requests, augmenter timeout

### Symptom: "Certain extensions don't fallback"
**Cause:** Extension config doesn't specify fallback
**Fix:** Ajouter "use_fallback: true" dans section extension

---

**Total Implementation Time: ~3-4 hours**
**Ongoing Maintenance: 15 min/week monitoring**
