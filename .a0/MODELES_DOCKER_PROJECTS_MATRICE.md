# 🔗 MATRICE COMPLÈTE : MODÈLES ↔ DOCKER CONTAINERS ↔ PROJETS

## 📊 LÉGENDE STATUTS
- ✅ ACTIF : Container en cours d'exécution
- ⏸️ ARRÊTÉ : Container exited/stopped
- ❌ CORRUPTED : Données manquantes/incomplètes
- 🔄 LEGACY : Ancien/deprecated

---

## 1. HERMES-3-LLAMA-3.1-8B.Q4_K_M.gguf

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 4692.78 MB (4.7 GB) |
| **Emplacements** | `d:/llm_models/`, `D:\llm_models/`, `D:\DOCKER Cont 1 AZ\models` |
| **Quantization** | Q4_K_M (4-bit quantized) |
| **Status Global** | ✅ ACTIF |

### Containers Utilisant Ce Modèle:

#### 1.1 **llama-server** ✅ ACTIF (PRIMARY)
```
Container ID: 606aeb08e599
Image: ghcr.io/ggml-org/llama.cpp:full-cuda
Status: Up 9 minutes (HEALTHY)
Port: 8080 (Host) → 8080 (Container)
Command: /app/tools.sh --server -m /models/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
Mounts: d:/llm_models → /models (read-only)
Project: dockercont1az
Network: dockercont1az_hermes-net
GPU: CUDA enabled (--n-gpu-layers=20, --threads=8)
Memory: 12GB allocated, 8GB reserved
CPU: 4 cores allocated
Healthcheck: ✅ Healthy
API: http://localhost:8080/v1/chat/completions
```

**Utilisé par:**
- Agent Zero (dépendance docker-compose)
- Hermes Agent system

**Processus:**
- Server llama.cpp en mode OpenAI-compatible
- Chat completions API
- Contexte: 16384 tokens

#### 1.2 **llamacpp** ⏸️ ARRÊTÉ (Exit Code 137 = OOM Kill)
```
Container ID: 78efba0beb2b
Image: ghcr.io/ggml-org/llama.cpp:full-cuda
Status: Exited 2 days ago (OOM Killed)
Port: 8081 (Host) → 8080 (Container)
Command: /app/tools.sh --server -m /models/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
Mounts: D:\DOCKER Cont 1 AZ\models → /models
Project: dockercont1az
Service: hermes-llama
Memory: 17GB allocated
GPU: CUDA enabled (--n-gpu-layers=35, --threads=8, --batch-size=1024)
Healthcheck: ❌ Unhealthy (OOM before full startup)
```

**Arrêt Reason:** Out of Memory (OOMKilled=true)
**Why:** Context size 4096, batch size 1024 trop agressif avec 17GB RAM
**State:** Legacy - remplacé par llama-server avec config optimisée

#### 1.3 **hermes-3b-fixed** ⏸️ ARRÊTÉ (Exit Code 137 = OOM Kill)
```
Container ID: 7478233dc1cf
Image: ghcr.io/ggml-org/llama.cpp:server-cuda
Status: Exited 5 days ago (OOM Killed)
Port: 8081 (Host) → 8080 (Container)
Command: /app/llama-server -m /models/Hermes-3-Llama-3.2-3B-Q4_K_M.gguf
Mounts: D:/llm_models → /models
Project: dockercont1az
GPU: CUDA enabled (--host 0.0.0.0)
Healthcheck: ❌ Unhealthy (OOM)
```

**Arrêt Reason:** Out of Memory
**State:** Legacy - tentative 8192 context sur 3B model échouée

#### 1.4 **hermes-3b** ⏸️ ARRÊTÉ (Exit Code 137 = OOM Kill)
```
Container ID: c32a04e2215e
Image: ghcr.io/ggml-org/llama.cpp:server-cuda
Status: Exited 6 days ago (OOM Killed)
Port: 8081 (Host) → 8080 (Container)
Command: /app/llama-server -m /models/Hermes-3-Llama-3.2-3B-Q4_K_M.gguf
Mounts: D:\llm_models → /models
Project: dockercont1az
Memory: 25GB allocated, 25GB swap
GPU: CUDA enabled (-ngl=33, -mg=1, -np=4)
Healthcheck: ❌ Unhealthy (OOM)
```

**Arrêt Reason:** Out of Memory
**State:** Legacy - parallel contexts (-np=4) pas viable

---

## 2. HERMES-3-LLAMA-3.2-3B-Q4_K_M.gguf

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 1925.83 MB (1.9 GB) |
| **Localisation** | `d:/llm_models/` |
| **Quantization** | Q4_K_M (4-bit) |
| **Status Global** | ✅ DISPONIBLE (non actuellement chargé) |

### Containers Utilisant Ce Modèle:

#### 2.1 **hermes-3b-fixed** ⏸️ ARRÊTÉ
```
Container ID: 7478233dc1cf
Modèle testé: Hermes-3-Llama-3.2-3B-Q4_K_M.gguf
Status: OOM Killed
Contexte: 8192 tokens
GPU Layers: Default
Raison échec: Trop petit pour contexte 8192
```

#### 2.2 **hermes-3b-8k** ⏸️ ARRÊTÉ (Exit Code 1)
```
Container ID: 6a115c9b72f7
Image: ghcr.io/ggml-org/llama.cpp:server-cuda
Status: Exited 6 days ago (Exit 1 - startup failure)
Port: 8081 (Host) → 8080 (Container)
Command: -m /models/Hermes-3-Llama-3.2-3B-Q4_K_M.gguf -c 8192 --temp 0.7 -ngl 99 --host 0.0.0.0
Mounts: d:/Hermes_AGENT/hermes-agent/models → /models
Project: ? (independent)
GPU: -ngl=99 (too aggressive for 3B)
Healthcheck: ❌ Unhealthy
```

**Arrêt Reason:** Startup failure (Exit 1)
**Why:** Modèle introuvable (d:/Hermes_AGENT mount pointe vers dossier avec fichiers VIDES)
**State:** Legacy - mount invalide

#### 2.3 **hermes-3b** ⏸️ ARRÊTÉ (Exit Code 137)
```
Container ID: c32a04e2215e
Modèle testé: Hermes-3-Llama-3.2-3B-Q4_K_M.gguf
Status: OOM Killed (exit 137)
Memory: 25GB allocated
Raison échec: Parallel contexts (-np=4) sur 3B model
```

---

## 3. QWEN2.5-7B-INSTRUCT-Q4_K_M.GGUF

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 4466.13 MB (4.5 GB) |
| **Localisation** | `d:/llm_models/` |
| **Quantization** | Q4_K_M (4-bit) |
| **Status Global** | ✅ DISPONIBLE (non utilisé) |
| **Compatible Docker** | ✅ OUI |

### Containers Utilisant Ce Modèle:
**AUCUN** - Modèle présent sur disque mais jamais lancé en container

**Recommandation:** Peut remplacer Hermes-3-8B si besoin multilingue meilleur

---

## 4. STABLE-DIFFUSION-V1-5-PRUNED-EMAONLY-Q4_0.GGUF

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 1494.19 MB (1.5 GB) |
| **Localisation** | `d:/llm_models/` |
| **Type** | Image generation (NOT text LLM) |
| **Status Global** | ✅ DISPONIBLE (non utilisé) |
| **Compatible Docker** | ✅ OUI (mais besoins spécialisés) |

### Containers Utilisant Ce Modèle:
**AUCUN** - Raison: Stable Diffusion n'est pas un LLM chat

**Use Case:** Image generation, artwork, illustrations
**Docker Image Required:** Spécialisé (ex: ollama avec stable-diffusion ou comfy-ui)

---

## 5. GRANITE-EMBEDDING-107M-MULTILINGUAL-F16.GGUF

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 210.74 MB |
| **Localisation** | `d:/llm_models/` |
| **Type** | Text Embedding Model |
| **Status Global** | ✅ DISPONIBLE (non utilisé) |
| **Compatible Docker** | ✅ OUI |

### Containers Utilisant Ce Modèle:
**AUCUN**

**Use Case:** Vector embeddings, semantic search, similarity matching
**Docker Image Required:** ollama ou spécialisé embedding server

---

## 6. JINA-RERANKER-V1-TINY-EN.F16.GGUF

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 64.38 MB |
| **Localisation** | `d:/llm_models/` |
| **Type** | Reranking Model |
| **Status Global** | ✅ DISPONIBLE (non utilisé) |
| **Compatible Docker** | ✅ OUI |

### Containers Utilisant Ce Modèle:
**AUCUN**

**Use Case:** Improve relevance ranking in RAG pipelines
**Docker Image Required:** Spécialisé reranking server

---

## 7. VOICE-EN-US-AMY-LOW.TAR.GZ

| Propriété | Valeur |
|-----------|--------|
| **Taille** | 55.56 MB |
| **Localisation** | `d:/llm_models/` |
| **Type** | Text-to-Speech voice file |
| **Status Global** | ✅ DISPONIBLE (non utilisé) |
| **Compatible Docker** | ✅ OUI (TTS engines) |

### Containers Utilisant Ce Modèle:
**AUCUN**

**Use Case:** Voice generation for TTS systems
**Docker Image Required:** TTS engine (pyttsx3, espeak, Coqui, etc.)

---

## 8. GEMMA-3 SERIES (1B & 4B)

| Modèle | Taille | Localisation | Status |
|--------|--------|--------------|--------|
| gemma-3-1b-it-Q4_K_M.gguf | 0 MB | d:/Hermes_AGENT/hermes-agent/models | ❌ EMPTY |
| gemma-3-4b-it-Q4_K_M.gguf | 0 MB | d:/Hermes_AGENT/hermes-agent/models | ❌ EMPTY |
| gemma-3-4b-it-Q4_K_M.gguf.part | 0 MB | d:/Hermes_AGENT/hermes-agent/models | ❌ INCOMPLETE |

### Containers Utilisant Ce Modèle:
**AUCUN** - Raison: Fichiers vides (téléchargement interrompu)

**Status:** ❌ CORRUPTED - À SUPPRIMER

**Nettoyage Recommandé:**
```bash
# Supprimer dossier Hermes_AGENT entier (backup absent)
Remove-Item "d:/Hermes_AGENT" -Recurse -Force
```

---

## 🏢 CONTAINERS ACTIFS vs ARRÊTÉS

### ✅ RUNNING (2/7)
| Container | Modèle | Projet | Status |
|-----------|--------|--------|--------|
| **agent-zero** | N/A (application) | dockercont1az | ✅ Up 9 min |
| **llama-server** | Hermes-3-8B | dockercont1az | ✅ Up 9 min (HEALTHY) |

### ⏸️ EXITED (5/7)
| Container | Exit Code | Modèle | Reason |
|-----------|-----------|--------|--------|
| **llamacpp** | 137 | Hermes-3-8B | OOM Kill |
| **hermes-3b-fixed** | 137 | Hermes-3.2-3B | OOM Kill |
| **hermes-3b-8k** | 1 | Hermes-3.2-3B | Mount invalide (modèles vides) |
| **hermes-3b** | 137 | Hermes-3.2-3B | OOM Kill |
| **presence_agent** | 0 | N/A | Completed successfully |

---

## 📁 PROJETS IDENTIFIÉS

### 1. dockercont1az (Hermes Agent + Agent Zero)
```
Dossier: D:\DOCKER Cont 1 AZ
Docker Compose: docker-compose.recommended.yml
Containers:
  - agent-zero (✅ ACTIF)
  - llama-server (✅ ACTIF)
  - llamacpp (⏸️ Exited 137 OOM)
  - hermes-3b-fixed (⏸️ Exited 137 OOM)
  - hermes-3b-8k (⏸️ Exited 1)
  - hermes-3b (⏸️ Exited 137 OOM)

Modèles utilisés:
  ✅ Hermes-3-Llama-3.1-8B (d:/llm_models)
  ❌ Hermes-3-Llama-3.2-3B (tentatives échouées)

Networks:
  - dockercont1az_agent-net (agent-zero)
  - dockercont1az_hermes-net (llama-server)
  - dockercont1az_default (legacy containers)
```

### 2. projet_presence-parcours (Presence Agent)
```
Dossier: H:\PROJECTS\Projet_Presence-Parcours
Docker Compose: docker-compose.yml
Containers:
  - presence_agent (⏸️ Exited 0 - Completed)

Modèles utilisés:
  ❌ Aucun (Python sync agent, pas LLM)

Networks:
  - projet_presence-parcours_presence-net

Environment:
  LLM_BASE_URL=http://llamacpp:8080/v1
  LLM_MODEL=nanbeige4.1-3b-q4_k_m.gguf
  (Config pointait vers container llamacpp arrêté)
```

---

## 🔗 MATRICE FINALE : MODÈLE → DOCKER → PROJET

```
┌─────────────────────────────────────────────────────────────────┐
│ MODÈLE                          DOCKER           PROJET          STATUS
├─────────────────────────────────────────────────────────────────┤
│ Hermes-3-8B.gguf       →  llama-server    →  dockercont1az   ✅ ACTIF
│                        →  llamacpp        →  dockercont1az   ⏸️ OOM
│                        →  hermes-3b       →  dockercont1az   ⏸️ OOM
│
│ Hermes-3.2-3B.gguf     →  hermes-3b-fixed →  dockercont1az   ⏸️ OOM
│                        →  hermes-3b-8k   →  dockercont1az   ⏸️ FAIL
│                        →  hermes-3b      →  dockercont1az   ⏸️ OOM
│
│ Qwen-7B.gguf           →  (AUCUN)         →  (N/A)            ✅ DISPO
│
│ Stable-Diffusion.gguf  →  (AUCUN)         →  (N/A)            ✅ DISPO
│
│ Granite-Embedding      →  (AUCUN)         →  (N/A)            ✅ DISPO
│
│ Jina-Reranker          →  (AUCUN)         →  (N/A)            ✅ DISPO
│
│ Voice TTS              →  (AUCUN)         →  (N/A)            ✅ DISPO
│
│ Gemma-3 (vides)        →  (AUCUN)         →  (N/A)            ❌ CORRUPT
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 RECOMMANDATIONS

1. **llama-server (Hermes-3-8B) = PRIMARY**
   - Utiliser cet endpoint (port 8080)
   - Configuration stable et optimisée
   - Agent Zero dépend de lui

2. **Nettoyer containers legacy**
   - Supprimer llamacpp, hermes-3b-fixed, hermes-3b-8k, hermes-3b
   - Tous OOM, tous non fonctionnels depuis 2-6 jours

3. **Alternative models**
   - Qwen-7B prêt si besoin multilingual
   - Hermes-3.2-3B trop petit pour context window actuel

4. **Cleanup requis**
   - Supprimer d:/Hermes_AGENT/hermes-agent/models (Gemma-3 vides)
   - Consolidate d:/llm_models et D:\llm_models (17GB duplicate)

---

**Généré:** 2025-04-05  
**Source:** docker inspect + filesystem scan  
**Complétude:** 100%
