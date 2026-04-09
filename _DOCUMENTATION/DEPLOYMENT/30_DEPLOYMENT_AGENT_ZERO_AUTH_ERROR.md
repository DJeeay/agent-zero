---
title: "Agent Zero Authentication Error - Rapport"
audience: ["Developer", "DevOps"]
level: "Advanced"
time_to_read: "20 min"
last_updated: "2025-04-05"
category: "DEPLOYMENT"
topic: "Authentication"
related_docs:
  - "../01_INDEX.md"
  - "31_DEPLOYMENT_LOCAL_SETUP.md"
  - "../OPERATIONS/20_OPERATIONS_COMMANDS.md"
  - "../REFERENCE/10_REFERENCE_CONTAINERS_ANALYSIS.md"
depends_on:
  - "Agent Zero"
  - "Docker"
  - "OpenRouter API"
---

# 📊 RAPPORT COMPLET - Agent Zero Authentication Error

## 🚨 PROBLÈME IDENTIFIÉ

### Erreur Récurrente
```
litellm.exceptions.AuthenticationError: OpenrouterException - {"error":{"message":"Missing Authentication header","code":401}}
```

### Source du Problème
- Agent Zero essaie d'utiliser OpenRouter pour l'extension "memorize solutions"
- L'API key OpenRouter n'est pas correctement chargée dans l'environnement Agent Zero
- Votre configuration PARAPLUIE vide l'API key pour forcer l'usage local, mais Agent Zero ne trouve pas de configuration alternative
- OpenRouter n'est pas accessible dans le contexte d'exécution d'Agent Zero

---

## 🔍 ANALYSE TECHNIQUE

### 1. Architecture Actuelle
| Composant | État | Problème |
|-----------|------|---------|
| Hermes Agent | ✅ Fonctionne | Utilise Gemma 270M local (port 8080) |
| Agent Zero | ❌ Erreur 401 | Essaie d'utiliser OpenRouter (échec) |
| Ollama | ✅ Disponible | Non configuré pour Agent Zero |

### 2. Points de Défaillance
```
❌ Variables d'environnement non héritées par Agent Zero
❌ Configuration Agent Zero absente ou incorrecte
❌ OpenRouter API key non accessible dans le contexte Agent Zero
❌ Fallback vers LLM local non configuré
```

### 3. Impact
- Extension "memorize solutions" ne fonctionne pas
- Agent Zero ne peut pas compléter ses tâches
- Perte de fonctionnalité critique pour les agents IA

---

## ✅ SOLUTION TECHNIQUE

### Stratégie d'Implémentation
```
1. Forcer Agent Zero à utiliser LLM local
2. Désactiver complètement OpenRouter dans Agent Zero
3. Configurer Ollama comme provider principal
4. Utiliser Llama 3.2 3B (performant et léger)
5. Maintenir compatibilité avec extensions existantes
```

---

## 📋 TO-DO LIST COMPLÈTE

### 🚨 PHASE 1 : DÉPLOIEMENT OLLAMA (URGENT - À FAIRE MAINTENANT)

#### Tâche 1.1 : Démarrer Ollama
**État :** ⏳ En attente  
**Commande :**
```bash
docker run -d --gpus=all \
    -v "${PWD}/ollama:/root/.ollama" \
    -p 11434:11434 \
    -p 8000:11434 \
    --restart unless-stopped \
    --name ollama \
    ollama/ollama
```

**Détails :**
- `--gpus=all` : Accès GPU NVIDIA (optionnel mais recommandé)
- `-v "${PWD}/ollama:/root/.ollama"` : Persistance des modèles
- `-p 11434:11434` : Port Ollama natif
- `-p 8000:11434` : Port alternatif pour compatibilité API

**Vérification :**
```bash
docker ps | grep ollama
```

---

#### Tâche 1.2 : Télécharger les Modèles
**État :** ⏳ En attente  
**Commandes :**
```bash
docker exec -it ollama ollama pull llama3.2:3b
docker exec -it ollama ollama pull phi3.5:3.8b
docker exec -it ollama ollama pull gemma2:2b
```

**Rationale :**
- `llama3.2:3b` : Modèle principal (équilibré performance/vitesse)
- `phi3.5:3.8b` : Alternative rapide et légère
- `gemma2:2b` : Backup pour ressources limitées

**Temps estimé :** 20-30 minutes (dépend vitesse Internet)

**Vérification :**
```bash
docker exec -it ollama ollama list
```

---

#### Tâche 1.3 : Tester Connectivité Ollama
**État :** ⏳ En attente  
**Commande :**
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Test de connexion"}],
    "stream": false
  }'
```

**Réponse attendue :**
```json
{
  "model": "llama3.2:3b",
  "created": 1234567890,
  "message": {
    "role": "assistant",
    "content": "Connexion réussie!"
  }
}
```

---

### 🔧 PHASE 2 : CONFIGURATION AGENT ZERO
**État :** ⏳ En attente  
**Fichier :** `~/.a0/config.yaml`

**Contenu :**
```yaml
# Configuration Agent Zero - Mode LLM Local
provider: "ollama"
model: "llama3.2:3b"

# Configuration Ollama
ollama:
  base_url: "http://localhost:8000"
  model: "llama3.2:3b"
  temperature: 0.7
  top_p: 0.9
  top_k: 40

# Désactiver OpenRouter complètement
openrouter:
  enabled: false
  api_key: ""

# Extensions
extensions:
  memorize_solutions:
    enabled: true
    provider: "ollama"
    model: "llama3.2:3b"

# Logging
logging:
  level: "INFO"
  file: "~/.a0/logs/agent_zero.log"
```

**Commande pour créer :**
```bash
mkdir -p ~/.a0
cat > ~/.a0/config.yaml << 'EOF'
provider: "ollama"
model: "llama3.2:3b"

ollama:
  base_url: "http://localhost:8000"
  model: "llama3.2:3b"
  temperature: 0.7
  top_p: 0.9
  top_k: 40

openrouter:
  enabled: false
  api_key: ""

extensions:
  memorize_solutions:
    enabled: true
    provider: "ollama"
    model: "llama3.2:3b"

logging:
  level: "INFO"
  file: "~/.a0/logs/agent_zero.log"
EOF
```

---

#### Tâche 2.2 : Configurer Variables d'Environnement
**État :** ⏳ En attente  
**Fichier :** `~/.a0/.env.local`

**Contenu :**
```bash
# Agent Zero Local Configuration
A0_PROVIDER=ollama
A0_MODEL=llama3.2:3b
A0_OLLAMA_BASE_URL=http://localhost:8000
A0_OPENROUTER_ENABLED=false
A0_OPENROUTER_API_KEY=""

# Désactiver complètement OpenRouter
OPENROUTER_API_KEY=""
```

**Commande pour créer :**
```bash
cat > ~/.a0/.env.local << 'EOF'
A0_PROVIDER=ollama
A0_MODEL=llama3.2:3b
A0_OLLAMA_BASE_URL=http://localhost:8000
A0_OPENROUTER_ENABLED=false
A0_OPENROUTER_API_KEY=""
OPENROUTER_API_KEY=""
EOF
```

---

### 🔄 PHASE 3 : REDÉMARRAGE ET VALIDATION

#### Tâche 3.1 : Arrêter Agent Zero
**État :** ⏳ En attente  
**Commande :**
```bash
# Trouver le processus
ps aux | grep "agent.zero\|a0" | grep -v grep

# Arrêter gracieusement (PID à remplacer)
kill -15 <PID>

# Ou via Docker si conteneurisé
docker stop agent-zero
docker rm agent-zero
```

---

#### Tâche 3.2 : Relancer Agent Zero
**État :** ⏳ En attente  
**Commande :**
```bash
# Vérifier la configuration est en place
cat ~/.a0/config.yaml

# Relancer Agent Zero (adapter selon votre setup)
cd /chemin/vers/agent-zero
python main.py --config ~/.a0/config.yaml

# OU via Docker
docker run -d \
  -v ~/.a0:/root/.a0 \
  -v ${PWD}/ollama:/root/.ollama \
  -p 8001:8000 \
  --name agent-zero \
  agent-zero:latest
```

---

#### Tâche 3.3 : Test Extension "Memorize Solutions"
**État :** ⏳ En attente  
**Procédure :**
1. Lancer Agent Zero
2. Exécuter une tâche qui utilise "memorize solutions"
3. Vérifier les logs pour absence d'erreur 401
4. Confirmer la réponse du modèle local

**Commande de test :**
```bash
# Vérifier logs
tail -f ~/.a0/logs/agent_zero.log

# Chercher absence de :
# - "401 Unauthorized"
# - "OpenrouterException"
# - "Missing Authentication header"

# Chercher présence de :
# - "Using Ollama provider"
# - "Model: llama3.2:3b"
# - "Extension memorize_solutions: active"
```

---

### ✔️ PHASE 4 : TESTS DE VALIDATION

#### Tâche 4.1 : Vérifier Processus Ollama
**État :** ⏳ En attente  
**Commandes :**
```bash
# Vérifier le container
docker ps | grep ollama
# Résultat attendu : container en état "Up"

# Vérifier modèles disponibles
docker exec -it ollama ollama list
# Résultat attendu : llama3.2:3b, phi3.5:3.8b, gemma2:2b listés

# Vérifier santé
docker inspect ollama --format='{{.State.Status}}'
# Résultat attendu : "running"
```

---

#### Tâche 4.2 : Test API Ollama Complet
**État :** ⏳ En attente  
**Commande :**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "user", "content": "Quel est 2+2?"}
    ],
    "stream": false
  }' | jq .
```

**Résultat attendu :**
```json
{
  "model": "llama3.2:3b",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "2+2 égale 4."
      }
    }
  ]
}
```

---

#### Tâche 4.3 : Vérifier Configuration Agent Zero
**État :** ⏳ En attente  
**Commandes :**
```bash
# Afficher configuration active
cat ~/.a0/config.yaml

# Afficher variables d'environnement
grep -E "A0_|OPENROUTER" ~/.a0/.env.local

# Vérifier pas d'API keys en dur
grep -i "api.key\|sk-" ~/.a0/config.yaml
# Résultat attendu : aucun résultat
```

---

#### Tâche 4.4 : Test Complet Agent Zero
**État :** ⏳ En attente  
**Procédure :**
1. Accéder à l'interface Agent Zero
2. Créer une tâche simple : "Résume ceci en français"
3. Observer les logs en temps réel
4. Vérifier réponse obtenue sans erreur 401
5. Confirmation : ✅ Extension "memorize solutions" fonctionne

**Commande surveillance logs :**
```bash
# Terminal 1 : Surveillance logs
tail -f ~/.a0/logs/agent_zero.log

# Terminal 2 : Lancer tâche test
# (via interface Agent Zero)

# Chercher dans logs :
# - "Using provider: ollama" ✅
# - "Model: llama3.2:3b" ✅
# - "memorize_solutions: processing" ✅
# - "401\|AuthenticationError\|OpenRouter" ❌ (ne doit PAS apparaître)
```

---

## 📊 MÉTRIQUES DE SUCCÈS

### Avant la Correction
| Métrique | État |
|----------|------|
| Erreur 401 OpenRouter | ❌ Systématique |
| Extension "memorize solutions" | ❌ Inopérante |
| Agent Zero fonctionnel | ❌ Bloqué |
| Latence réseau | ❌ Présente |
| Coûts API | ❌ Charges OpenRouter |

### Après la Correction (Attendu)
| Métrique | État |
|----------|------|
| Erreur 401 OpenRouter | ✅ Aucune |
| Extension "memorize solutions" | ✅ Fonctionnelle |
| Agent Zero fonctionnel | ✅ Pleinement opérationnel |
| Latence réseau | ✅ Nulle (traitement local) |
| Coûts API | ✅ Zéro (infrastructure locale) |

---

## 🎯 BÉNÉFICES DE LA SOLUTION

### Avantages Techniques
| Bénéfice | Impact |
|----------|--------|
| **Fiabilité** | Plus de dépendances externes (pas de panne OpenRouter) |
| **Performance** | Traitement local instantané vs latence réseau |
| **Sécurité** | Données ne quittent jamais votre machine |
| **Coût** | Zéro frais d'API (infrastructure déjà payée) |
| **Contrôle** | Maîtrise totale des modèles utilisés |

### Avantages Opérationnels
| Aspect | Gain |
|--------|------|
| **Autonomie** | Fonctionnement hors-ligne possible |
| **Scalabilité** | Possibilité d'upgrader modèles localement |
| **Maintenance** | Pas de dépendances tier-3 |
| **Debugging** | Logs locaux complets |

---

## 📋 CHECKLIST FINALE

### Phase 1 : Infrastructure
- [ ] **1.1** Ollama démarré et accessible sur http://localhost:8000/v1
- [ ] **1.2** Modèles téléchargés (llama3.2:3b minimum)
- [ ] **1.3** Test API Ollama réussi

### Phase 2 : Configuration
- [ ] **2.1** Configuration Agent Zero créée (~/.a0/config.yaml)
- [ ] **2.2** Variables d'environnement forcées vers LLM local (~/.a0/.env.local)
- [ ] **2.3** Vérification : aucune API key OpenRouter en dur

### Phase 3 : Déploiement
- [ ] **3.1** Agent Zero arrêté proprement
- [ ] **3.2** Agent Zero relancé avec nouvelle configuration
- [ ] **3.3** Extension "memorize solutions" fonctionnelle

### Phase 4 : Validation
- [ ] **4.1** Processus Ollama actif (docker ps)
- [ ] **4.2** Modèles listés correctement
- [ ] **4.3** Test API Ollama réussi
- [ ] **4.4** Test complet Agent Zero sans erreur 401
- [ ] **4.5** Monitoring : logs confirment utilisation locale

---

## 🚨 POINTS D'ATTENTION

### Prérequis Hardware
| Ressource | Minimum | Recommandé |
|-----------|---------|-----------|
| **RAM** | 8 GB | 16 GB |
| **GPU** | CPU suffisant | NVIDIA avec CUDA |
| **Disque** | 20 GB | 50 GB |

### Prérequis Software
```bash
# Vérifier Docker installé
docker --version

# Vérifier accès GPU (si applicable)
docker run --rm --gpus all ubuntu nvidia-smi

# Vérifier ports libres
netstat -tulpn | grep -E "8000|11434"
# Résultat attendu : aucun processus en écoute
```

### Dépannage Courant

**Symptôme :** Container Ollama ne démarre pas
```bash
# Solution
docker logs ollama
docker run -it ollama/ollama bash
```

**Symptôme :** Modèles ne téléchargent pas
```bash
# Solution : Vérifier connectivité
docker exec ollama curl -I https://registry.ollama.ai
# Aumenter timeout
docker exec -it ollama timeout 3600 ollama pull llama3.2:3b
```

**Symptôme :** Port 8000 déjà utilisé
```bash
# Solution : Utiliser port alternatif
docker run -d ... -p 8001:11434 ... ollama/ollama
# Puis mettre à jour config Agent Zero : base_url: "http://localhost:8001"
```

---

## 🎉 RÉSULTAT FINAL ATTENDU

### État Système Après Completion
```
✅ Ollama actif et accessible (port 8000/11434)
✅ Modèles llama3.2:3b, phi3.5:3.8b, gemma2:2b téléchargés
✅ Agent Zero configuré pour LLM local
✅ Extension "memorize solutions" opérationnelle
✅ Zéro erreur d'authentification OpenRouter
✅ Performance améliorée (traitement local)
✅ Infrastructure entièrement autonome
```

### Logs Attendus dans ~/ a0/logs/agent_zero.log
```
[INFO] Agent Zero initialization
[INFO] Loading configuration from ~/.a0/config.yaml
[INFO] Provider: ollama
[INFO] Model: llama3.2:3b
[INFO] Ollama base_url: http://localhost:8000
[INFO] OpenRouter: DISABLED
[INFO] Extension 'memorize_solutions' loaded
[INFO] Ready to accept tasks
```

### Commande de Monitoring en Temps Réel
```bash
# Terminal 1 : Monitoring Ollama
docker stats ollama

# Terminal 2 : Monitoring Agent Zero
tail -f ~/.a0/logs/agent_zero.log

# Terminal 3 : Test d'une tâche
# (via interface Agent Zero)
```

---

## 📞 SUPPORT & ESCALADE

Si un test échoue à une phase :
1. Relire la section "Dépannage Courant"
2. Vérifier les commandes exactes (copier-coller)
3. Consulter les logs détaillés
4. Reporter erreur spécifique avec logs complets

---

**Document généré :** 2025-01-XX  
**Version :** 1.0  
**Statut :** À exécuter
