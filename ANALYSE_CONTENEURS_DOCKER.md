# Analyse Technique des Conteneurs Docker Actifs

---

## 📋 Introduction pour Non-Techniciens

### Qu'est-ce que Docker ?

Docker est une technologie qui permet de **créer et exécuter des applications dans des "conteneurs"** — penser à des boîtes isolées contenant tout ce dont une application a besoin pour fonctionner (code, fichiers, dépendances, configurations).

**Avantages** :
- ✅ Isolation : chaque application fonctionne dans son propre environnement sans interférer avec les autres
- ✅ Portabilité : une application fonctionne identiquement sur n'importe quel ordinateur
- ✅ Efficacité : utilise moins de ressources qu'une machine virtuelle classique

### Ce que vous verrez dans ce rapport

Ce document liste les **conteneurs en cours d'exécution**, leurs **ressources consommées**, leurs **configurations réseau**, et identifie les conteneurs **arrêtés ou défaillants**.

---

## 🟢 Conteneurs Actifs (En Cours d'Exécution)

### 1. **LlamaCpp Server (Principal)** — Port 8080
- **Image** : `ghcr.io/ggml-org/llama.cpp:full-cuda`
- **Nom** : `llama-server`
- **ID Complet** : `94e3c14e3be1`
- **Statut** : ✅ **En cours d'exécution depuis 26 heures** (sain)
- **Accès** : http://localhost:8080
- **Type** : Serveur d'inférence IA (LLM - Large Language Model)
- **Modèle** : `Hermes-3-Llama-3.1-8B.Q4_K_M.gguf`
- **Description** : Serveur d'inférence pour modèles de langage optimisé avec GPU CUDA NVIDIA

**Configuration Technique** :
- **Mémoire allouée** : Illimitée (Memory: 0 = non limité)
- **CPU** : 4 cores réservés (4000000000 NanoCpus = 4.0 CPUs)
- **GPU** : 1x GPU NVIDIA (DeviceCount: 1, `CUDA_VISIBLE_DEVICES=0`)
- **Context Window** : 16384 tokens
- **GPU Layers** : 20 couches (sur ~32 total) → Offload GPU optimal
- **Threads** : 8 CPU threads
- **Volume** : Mount RO (lecture seule) sur `d:/llm_models`

**Métadonnées Réseau** :
- Port TCP : `0.0.0.0:8080 ↔ conteneur:8080`
- Réseaux : `hermes-agent_default` (bridge)
- IP Conteneur : `172.19.0.3`
- Protocole : HTTP
- Health Check : ✅ OK (curl sur `/health`, interval 10s, timeout 5s)
- Restart Policy : `unless-stopped` (redémarrage automatique en cas de crash)

---

### 2. **LlamaCpp Backup** — Port 8081
- **Image** : `ghcr.io/ggml-org/llama.cpp:full-cuda`
- **Nom** : `llamacpp` (service Docker Compose : `hermes-llama`)
- **ID Complet** : `78efba0beb2b`
- **Statut** : ✅ **En cours d'exécution depuis 26 heures** (sain)
- **Accès** : http://localhost:8081
- **Type** : Serveur d'inférence IA (Configuration Alternative/Test)
- **Modèle** : `Hermes-3-Llama-3.1-8B.Q4_K_M.gguf` (même que le principal)
- **Description** : Serveur de secours avec configuration optimisée pour throughput élevé

**Configuration Technique** :
- **Mémoire allouée** : **16 GB** (hard limit: 17179869184 bytes)
- **Mémoire réservée** : 8 GB (soft limit)
- **Swap** : 32 GB
- **CPU** : 4 cores réservés (4000000000 NanoCpus)
- **GPU** : Tous les GPUs disponibles (DeviceCount: -1 = tous)
- **Context Window** : 4096 tokens
- **GPU Layers** : 35 couches (plus agressif que le principal)
- **Batch Size** : 1024 (optimisé pour parallélisme)
- **Threads** : 8 CPU threads
- **Volume** : Mount RW sur `D:\\DOCKER Cont 1 AZ\\models`

**Métadonnées Réseau** :
- Port TCP : `0.0.0.0:8081 ↔ conteneur:8080`
- Réseaux : `dockercont1az_default` + `agent-zero-network` (dual network)
- IP Conteneur (dockercont1az) : `172.19.0.2`
- IP Conteneur (agent-zero) : `172.23.0.3`
- Protocole : HTTP
- Health Check : ✅ OK (curl sur `/health`, interval 30s, timeout 10s)
- Restart Policy : `unless-stopped`

**🔍 Note Importante** : Configuration **différente du principal** malgré le même modèle :
- **Batch Size 1024** (principal n'en a pas) → meilleur throughput
- **GPU Layers 35** (vs 20) → plus de VRAM utilisée mais plus rapide
- **Context 4096** (vs 16384) → économies mémoire
- **Mémoire contrôlée à 16 GB** → limite claire (vs illimitée pour le principal)
- **Dual network** (agent-zero + dockercont1az) → probablement orchestré par Agent-Zero et docker-compose

---

### 3. **Agent-Zero** — Port 50080
- **Image** : `agent0ai/agent-zero:latest`
- **Nom** : `agent-zero`
- **ID Complet** : `75ba06ff16a1`
- **Statut** : ✅ **En cours d'exécution depuis 25 heures**
- **Accès** : http://localhost:50080
- **Type** : Agent IA autonome (orchestrateur de tâches)
- **Description** : Agent capable de prendre des décisions et d'orchestrer les serveurs LLM

**Configuration Technique** :
- **Mémoire** : Non limitée
- **GPU** : Pas accès GPU direct (appels API vers les serveurs LLM)
- **Volume** : `AGENT0Volume` (stockage persistant pour l'état agent)
- **Réseau** : `agent-zero-network` (bridge isolé)

**Métadonnées Réseau** :
- Port TCP : `0.0.0.0:50080 ↔ conteneur:80`
- Réseau : `agent-zero-network` (bridge isolé)
- IP Conteneur : `172.23.0.2`
- Protocole : HTTP
- Restart Policy : Défaut (pas redémarrage auto)

**Intégration** :
- Agent-Zero peut **appeler les serveurs LLM** via le réseau bridge `agent-zero-network`
- Les deux serveurs LlamaCpp sont connectés à ce réseau, il peut donc les orchestrer

---

## 🔴 Conteneurs Arrêtés ou En Erreur

| Nom | Image | Statut | Arrêté il y a | Code Erreur |
|-----|-------|--------|---------------|-------------|
| `hermes-3b-fixed` | `ghcr.io/ggml-org/llama.cpp:server-cuda` | Exited | 3 jours | **137** (OOM/Timeout) |
| `hermes-3b-8k` | `ghcr.io/ggml-org/llama.cpp:server-cuda` | Exited | 4 jours | **1** (Erreur générale) |
| `hermes-3b` | `ghcr.io/ggml-org/llama.cpp:server-cuda` | Exited | 4 jours | **137** (OOM/Timeout) |
| `presence_llamacpp` | `localai/localai:latest-aio-gpu-nvidia-cuda-12` | Exited | 12 jours | **128** (Signal invalide) |
| `presence_agent` | `5d7e0f0cfe08` (custom) | Exited | 12 jours | **0** (Arrêt normal) |

### 🔍 Interprétation des Codes d'Erreur

- **Code 137** : Le conteneur a été arrêté du fait d'une **manque de mémoire (OOM - Out Of Memory)** ou d'un timeout système
  - 💡 Action recommandée : augmenter les limites mémoire ou optimiser le modèle/configuration
  
- **Code 1** : **Erreur générale** — le processus a échoué
  - 💡 Action recommandée : consulter les logs avec `docker logs hermes-3b-8k`
  
- **Code 128** : **Signal invalide ou problème système**
  - 💡 Action recommandée : vérifier la configuration GPU/drivers

- **Code 0** : **Arrêt volontaire normal** — conteneur arrêté manuellement ou par une orchestration

---

## 💾 Ressources Docker

### Volumes (Stockage Persistant)

**Total** : 30 volumes détectés

**Volumes nommés** :
- `AGENT0Volume` — Volume associé à Agent-Zero (stockage persistant pour l'agent)

**Volumes anonymes** : 29 volumes générés automatiquement (identifiants SHA256)
- Ces volumes sont associés à différents conteneurs et contiennent des données persistantes (modèles IA, configurations, bases de données)

### Réseaux Docker

**Total** : 9 réseaux détectés

**Réseaux personnalisés (bridge)** :
1. `agent-zero-network` — Réseau isolé pour Agent-Zero
2. `dockercont1az_default` — Réseau par défaut d'un composé Docker
3. `hermes-agent_default` — Réseau pour les conteneurs Hermes
4. `hermes-agent_hermes-net` — Réseau personnalisé du groupe Hermes
5. `projet_presence-parcours_presence-net` — Réseau pour le projet Presence-Parcours
6. `run_default` — Réseau de runtime par défaut

**Réseaux système** :
- `host` — Accès direct au réseau de l'hôte
- `bridge` — Réseau par défaut de Docker
- `none` — Aucune connectivité réseau

---

## 🔗 Architecture Réseau & Orchestration Réelle

```
┌──────────────────────────────────────────────────────────┐
│              Hôte (Windows + Docker Desktop)             │
│                 NVIDIA GPU Support                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │   agent-zero-network (bridge isolé)            │    │
│  │                                                 │    │
│  │  [Agent-Zero] (port 50080)     [llamacpp]      │    │
│  │    172.23.0.2                 172.23.0.3      │    │
│  │    (Pas GPU)                  (GPU: tous)      │    │
│  │    Orchestrateur              16GB mem limit   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  dockercont1az_default (docker-compose)        │    │
│  │                                                 │    │
│  │     [llama-server]  (port 8080)                │    │
│  │       172.19.0.3                               │    │
│  │       GPU: 1 (CUDA_VISIBLE_DEVICES=0)         │    │
│  │       Mem: Illimitée                           │    │
│  │       Ctx: 16384, GPU-layers: 20              │    │
│  │       (Latence basse, long context)            │    │
│  │                                                 │    │
│  │     [llamacpp] (port 8081)                    │    │
│  │       172.19.0.2                               │    │
│  │       GPU: tous (-1)                           │    │
│  │       Mem: 16GB limit                          │    │
│  │       Ctx: 4096, GPU-layers: 35               │    │
│  │       Batch: 1024                              │    │
│  │       (Throughput élevé, compact)              │    │
│  │                                                 │    │
│  │     (Service Docker Compose: hermes-llama)    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Stockage Persistant:                                   │
│  - AGENT0Volume → État Agent-Zero                       │
│  - D:\DOCKER Cont 1 AZ\models → Modèles LLM (RW)      │
│  - d:/llm_models → Modèles LLM (RO)                   │
│                                                          │
└──────────────────────────────────────────────────────────┘

Flux de Communication:
  Client → :8080 → llama-server (contexte long)
  Client → :8081 → llamacpp (parallélisation)
  Client → :50080 → Agent-Zero (orchestration)
  Agent-Zero ←→ llamacpp (intra-réseau 172.23.0.0/16)
```

---

## 📊 Synthèse des Ressources

| Métrique | Valeur |
|----------|--------|
| **Conteneurs Actifs** | 3 |
| **Conteneurs Arrêtés** | 5 |
| **Volumes** | 30 |
| **Réseaux Personnalisés** | 6 |
| **Réseaux Système** | 3 |
| **Uptime Maximal** | 26 heures |
| **Services IA Actifs** | 2 (LlamaCpp serveurs) + 1 Agent |

---

## 🚨 Points Critiques à Adresser (RÉALITÉ TECHNIQUE)

### 1. **🔴 CONTENTION GPU ENTRE DEUX SERVEURS LlamaCpp**

**Problématique** :
- **llamacpp** (port 8081) : `DeviceCount: -1` = **TOUS les GPUs disponibles**
- **llama-server** (port 8080) : `CUDA_VISIBLE_DEVICES=0` = **GPU 0 uniquement**
- **Impact** : Les deux serveurs rivalisent pour les mêmes ressources GPU si vous avez 1-2 GPUs

**Diagnostic** :
```bash
# Vérifier l'utilisation GPU en temps réel
nvidia-smi           # Si disponible
nvidia-smi dmon -s pucvmet  # Mode stream (10x par sec)

# Ou dans le conteneur
docker exec llamacpp nvidia-smi
```

**Solutions** :

**Option A** (Recommandée) : Spécifier explicitement les GPUs
```bash
# llamacpp = GPU 1 (ou inutiliser si vous n'avez qu'un GPU)
docker update --gpus '"device=1"' llamacpp

# Ou arrêter ce service et ne garder que llama-server
docker stop llamacpp
docker update --restart no llamacpp  # Désactiver redémarrage auto
```

**Option B** (Load-balancing) : Utiliser Nginx pour partager les requêtes
```yaml
# docker-compose.yml (section nginx)
services:
  nginx-lb:
    image: nginx:latest
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - llama-server
      - llamacpp
```

Fichier `nginx.conf` :
```nginx
http {
  upstream llm_backend {
    server llama-server:8080 weight=1;  # Plus de latence mais contexte long
    server llamacpp:8080 weight=2;      # Plus de throughput
  }
  
  server {
    listen 80;
    location / {
      proxy_pass http://llm_backend;
      proxy_set_header Host $host;
    }
  }
}
```

**Mon Avis** : 
- Si vous avez **1 GPU** : **arrêter llamacpp** (option A)
- Si vous avez **2+ GPUs** : **assigner GPU 1 à llamacpp** (option A)
- Si vous testez des configurations : **faire du load-balancing** (option B)

---

### 2. **🔴 Conteneurs Hermes Arrêtés Depuis 3-12 Jours (OOM)**

**Fait** : 5 conteneurs morts
- `hermes-3b-fixed` : Code 137 (OOM) depuis 3 jours
- `hermes-3b` : Code 137 (OOM) depuis 4 jours  
- `hermes-3b-8k` : Code 1 (erreur générale) depuis 4 jours
- `presence_llamacpp` : Code 128 (signal invalide) depuis 12 jours
- `presence_agent` : Code 0 (arrêt volontaire) depuis 12 jours

**Diag** : Les codes 137 = **out-of-memory (OOM)**. Les modèles Hermes-3-Llama-3.1-8B consomment **trop de mémoire sans limite**.

**Solution Rapide** :
```bash
# Voir pourquoi ils se sont arrêtés
docker logs hermes-3b-fixed --tail 50  # Voir les 50 derniers logs
docker logs hermes-3b-8k --tail 50

# Redémarrer avec config fixée
docker update \
  --memory 12g \
  --memory-swap 24g \
  --restart unless-stopped \
  hermes-3b-fixed

docker start hermes-3b-fixed
```

**Mieux : Créer une docker-compose stable**
```yaml
version: '3.8'
services:
  hermes:
    image: ghcr.io/ggml-org/llama.cpp:server-cuda
    ports:
      - "8082:8080"
    volumes:
      - d:/llm_models:/models:ro
    environment:
      CUDA_VISIBLE_DEVICES: 0
    command: >
      --server
      -m /models/Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
      --host 0.0.0.0
      --port 8080
      --ctx-size 4096
      --n-gpu-layers 25
      --threads 8
    deploy:
      resources:
        limits:
          memory: 12G
        reservations:
          memory: 8G
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

### 3. **🏠 30 Volumes Orphelins = Consommation Disque**

**Faits** :
- 30 volumes Docker (plupart sont des SHA256 anonymes)
- 1 seul volume nommé : `AGENT0Volume` (celui d'Agent-Zero)
- Environ 25 volumes inutilisés (orphelins)

**Espace Occupé** :
```bash
docker system df       # Voir l'espace par type
```

**Solution** :
```bash
# Afficher les volumes inutilisés (dangling)
docker volume ls --filter dangling=true

# Supprimer les volumes orphelins
docker volume prune
# Répond : "WARNING! This will remove all dangling volumes."

# Nettoyage complet (ATTENTION: destructif)
docker system prune -a --volumes
```

---

### 4. **🔥 Deux Serveurs LlamaCpp en Production = Risque Instabilité**

**Réalité** :
- `llama-server` : **Pas de limite mémoire** (Memory: 0) → peut crasher le système
- `llamacpp` : **16GB limitée** mais DeviceCount -1 → peut monopoliser le GPU
- **Health checks actifs** mais sans redémarrage auto sur llama-server

**Risque** :
- Si `llama-server` consomme 20 GB RAM → crash du système Windows
- Si `llamacpp` monopolise GPU → `llama-server` ralentit
- Agent-Zero attend des réponses → timeout

**Fix Immédiat** :
```bash
# 1. Limiter llama-server
docker update \
  --memory 12g \
  --memory-swap 24g \
  --cpus 4 \
  llama-server

# 2. Spécifier le GPU pour llamacpp
docker update --gpus '"device=1"' llamacpp
# OU simplement l'arrêter
docker stop llamacpp

# 3. Assurer le redémarrage auto
docker update --restart unless-stopped llama-server
docker update --restart unless-stopped agent-zero
```

---

## 📈 Recommandations

### Court Terme
1. **Redémarrer les conteneurs défaillants** avec des configurations ajustées
2. **Monitorer les logs** : `docker logs -f llama-server`
3. **Vérifier l'espace disque** : `df -h` ou `docker system df`

### Moyen Terme
1. **Implémenter un système de monitorage** (Prometheus + Grafana)
2. **Configurer des health checks** explicites dans les conteneurs
3. **Automatiser les redémarrages** avec des politiques de restart (`--restart unless-stopped`)

### Long Terme
1. **Orchestration** : Considérer Kubernetes ou Docker Swarm pour la gestion multi-conteneurs
2. **Backup Automatique** : Définir une stratégie de sauvegarde pour les volumes
3. **Alertes** : Configurer des notifications en cas d'arrêt imprévu

---

## 🛠️ Commandes Utiles

### Inspection
```bash
# Afficher tous les conteneurs
docker ps -a

# Voir les détails d'un conteneur
docker inspect <container_id>

# Voir les logs
docker logs -f <container_name>

# Voir les statistiques (CPU, mémoire, réseau)
docker stats <container_name>
```

### Gestion
```bash
# Démarrer/arrêter un conteneur
docker start <container_id>
docker stop <container_id>

# Redémarrer
docker restart <container_id>

# Voir les volumes
docker volume ls
docker volume inspect <volume_name>

# Nettoyer les ressources inutilisées
docker system prune -a
```

---

**Généré le** : 2024  
**Système** : Docker Engine (Linux)  
**Accès réseau** : Localhost + Réseau local

