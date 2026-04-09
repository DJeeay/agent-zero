# 🎯 QUICK REFERENCE CARD - MODÈLES & DOCKER
## Pour consultation rapide - À afficher en permanence

---

## ❓ JE ME DEMANDE... PUIS-JE UTILISER CE MODÈLE EN DOCKER?

### ✅ OUI
| Modèle | Docker | Où? | Comment? |
|--------|--------|-----|----------|
| **Hermes-3-8B** | ✅ | llama-server:8080 | ACTIF MAINTENANT |
| **Hermes-3.2-3B** | ✅ | docker run (custom) | Disponible,jamais utilisé |
| **Qwen-7B** | ✅ | docker run (custom) | Disponible, jamais utilisé |
| **Granite-Embedding** | ✅ | docker run (custom) | Pour embeddings uniquement |
| **Jina-Reranker** | ✅ | docker run (custom) | Pour reranking uniquement |
| **Voice TTS** | ✅ | docker run (TTS engine) | Pour audio uniquement |

### ❌ NON
| Modèle | Raison | Status |
|--------|--------|--------|
| **Stable-Diffusion** | Image generation ≠ LLM | ❌ Pas de chat |
| **Gemma-3 (vides)** | Fichiers corrompus/vides | ❌ À supprimer |

---

## ❓ QUEL MODÈLE POUR QUELLE TÂCHE?

| Besoin | Modèle | Performant? | Recommandation |
|--------|--------|-------------|-----------------|
| **Chat/Text Generation** | Hermes-3-8B | ⭐⭐⭐⭐⭐ | ✅ Utiliser MAINTENANT (8080) |
| **Chat léger/rapide** | Hermes-3.2-3B | ⭐⭐⭐⭐ | ✅ Alternative si perfo manque |
| **Chat multilingue** | Qwen-7B | ⭐⭐⭐⭐⭐ | ✅ Meilleur pour non-English |
| **Vector Embeddings** | Granite-107M | ⭐⭐⭐⭐ | ✅ Pour RAG/search |
| **Relevance Ranking** | Jina-Reranker | ⭐⭐⭐⭐ | ✅ Pour RAG quality |
| **Text-to-Speech** | Voice TTS | ⭐⭐⭐ | ✅ Pour audio output |
| **Image Generation** | Stable-Diffusion | ⭐⭐⭐⭐ | ⚠️ Différent pipeline |

---

## ❓ OÙ EST LE MODÈLE X?

### Localisation Modèles

```
d:/llm_models/                          [PRINCIPAL - 13.5 GB]
├── Hermes-3-Llama-3.1-8B.Q4_K_M.gguf   ← llama-server l'utilise
├── Hermes-3-Llama-3.2-3B-Q4_K_M.gguf
├── Qwen2.5-7b-instruct-q4_k_m.gguf
├── Stable-Diffusion-v1-5-pruned-emaonly-Q4_0.gguf
├── Granite-embedding-107m-multilingual-f16.gguf
├── Jina-reranker-v1-tiny-en.f16.gguf
└── Voice-en-us-amy-low.tar.gz

D:\DOCKER Cont 1 AZ\models\             [BACKUP - Hermes-3-8B copy]
D:\llm_models\                          [ANCIEN - 13.5 GB doublon]

d:/Hermes_AGENT/hermes-agent/models\   [❌ VIDES - À SUPPRIMER]
```

---

## ❓ QUEL DOCKER CONTAINER UTILISE CE MODÈLE?

### Active Containers

```
🟢 llama-server (RUNNING)
   └─ Modèle: Hermes-3-8B
   └─ Port: 8080
   └─ API: http://localhost:8080/v1/chat/completions
   └─ Status: HEALTHY ✅
   └─ Projet: dockercont1az

🔴 agent-zero (RUNNING)
   └─ Modèle: N/A (application)
   └─ Port: 50080 (web UI)
   └─ Dépend de: llama-server:8080
   └─ Status: UP ✅
   └─ Projet: dockercont1az
```

### Exited Containers (À Ignorer)

```
❌ llamacpp (Exited 137 OOM) - Legacy
❌ hermes-3b (Exited 137 OOM) - Legacy
❌ hermes-3b-fixed (Exited 137 OOM) - Legacy
❌ hermes-3b-8k (Exited 1) - Legacy, mount invalide
❌ presence_agent (Exited 0) - Complété
```

---

## ❓ QUEL CONTENEUR POUR QUEL PROJET?

```
📂 dockercont1az/
   ├─ agent-zero (web UI + IA agent)
   └─ llama-server (LLM inference - Hermes-3-8B)
   
📂 Projet_Presence-Parcours/
   └─ presence_agent (completé - pas de modèle actif)
```

---

## ❓ JE VEUX CHARGER UN NOUVEAU MODÈLE - COMMENT?

### Pour Hermes-3.2-3B (léger, rapide)
```bash
docker run -d \
  --gpus=all \
  -v "d:/llm_models:/models:ro" \
  -p 8081:8080 \
  --name hermes-3b-light \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  /app/tools.sh --server \
  -m /models/Hermes-3-Llama-3.2-3B-Q4_K_M.gguf \
  --port 8080 --n-gpu-layers 20 --threads 8
```

### Pour Qwen-7B (multilingue)
```bash
docker run -d \
  --gpus=all \
  -v "d:/llm_models:/models:ro" \
  -p 8082:8080 \
  --name qwen-7b \
  ghcr.io/ggml-org/llama.cpp:full-cuda \
  /app/tools.sh --server \
  -m /models/Qwen2.5-7b-instruct-q4_k_m.gguf \
  --port 8080 --n-gpu-layers 20 --threads 8
```

---

## ❓ EST-CE QUE TOUS LES MODÈLES SONT COMPATIBLES DOCKER?

| Modèle | Compatibilité | Quel Docker? |
|--------|---------------|------------|
| Hermes-3-8B | ✅ OUI | ghcr.io/ggml-org/llama.cpp:full-cuda |
| Hermes-3.2-3B | ✅ OUI | ghcr.io/ggml-org/llama.cpp:full-cuda |
| Qwen-7B | ✅ OUI | ghcr.io/ggml-org/llama.cpp:full-cuda |
| Stable-Diffusion | ⚠️ OUI (mais) | comfy-ui ou spécialisé image engine |
| Granite-Embedding | ✅ OUI | ollama ou embedding server |
| Jina-Reranker | ✅ OUI | spécialisé reranking server |
| Voice TTS | ✅ OUI | pyttsx3, espeak, Coqui-TTS, etc. |
| Gemma-3 | ❌ NON | Fichiers vides/corrompus |

---

## ❓ QUEL CONTENEUR EST EN TRAIN DE TOURNER MAINTENANT?

```bash
docker ps
```

**Résultat attendu:**
```
NAMES          STATUS
agent-zero     Up 9 minutes
llama-server   Up 9 minutes (healthy)
```

---

## ❓ DOIS-JE CRÉER UN NOUVEAU CONTENEUR?

| Scenario | Action |
|----------|--------|
| Utiliser Hermes-3-8B | ❌ NON - llama-server existe déjà ✅ |
| Charger Hermes-3.2-3B | ✅ OUI - créer nouveau container (hermes-3b-light) |
| Charger Qwen-7B | ✅ OUI - créer nouveau container (qwen-7b) |
| Charger Embedding | ✅ OUI - créer service spécialisé |
| Embedding + Reranker | ✅ OUI - conteneurs séparés ou combined |
| Image generation | ✅ OUI - conteneur spécialisé (pas llama.cpp) |

---

## 🚀 COMMANDES RAPIDES

### Vérifier state actuel
```bash
docker ps
docker exec llama-server curl http://localhost:8080/health
curl http://localhost:8080/api/tags
```

### Tester modèle actuel
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "hermes-3-llama-3.1-8b",
    "messages": [{"role": "user", "content": "Test"}],
    "stream": false
  }'
```

### Voir logs modèle
```bash
docker logs -f llama-server
```

### Redémarrer llama-server
```bash
docker restart llama-server
```

---

## 📍 FICHIERS DE REFERENCE

Consultez ces fichiers pour plus de détails:

- `.a0/MODELES_INVENTAIRE_COMPLET.txt` - Full inventory de tous les modèles
- `.a0/MODELES_DOCKER_PROJECTS_MATRICE.md` - Matrice complète modèles↔docker↔projets
- `.a0/containers_full_inspect.json` - JSON brut de docker inspect

---

**GOLDEN RULE:**
Avant de lancer une commande Docker, consultez d'abord:
1. Est-ce que le modèle existe? (inventaire)
2. Est-ce qu'il y a déjà un container? (ps)
3. Quel est son port/endpoint? (matrice)
4. Quel est le projet associé? (matrice)

Ne plus demander "où est le modèle?" - c'est documenté ici.
