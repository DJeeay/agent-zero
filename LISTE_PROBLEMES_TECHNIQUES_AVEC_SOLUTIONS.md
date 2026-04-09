# 🔧 LISTE COMPLÈTE DES PROBLÈMES TECHNIQUES
## Diagnostic, Priorités et Solutions

---

## 📊 RÉSUMÉ EXÉCUTIF

| Catégorie | Nombre | Criticité | Délai |
|-----------|--------|-----------|-------|
| 🚨 Critiques (Bloquants) | 3 | URGENT | Immédiat |
| ⚠️ Mineurs (Gênants) | 3 | MOYEN | 24h |
| 🔍 Latents (Potentiels) | 3 | BAS | 1 semaine |
| 🏗️ Architecturaux | 3 | STRATÉGIQUE | Planifié |
| **TOTAL** | **12** | | |

**Estimation effort total :** 4-6 heures (plupart en parallèle)  
**Coût:** Zéro (infrastructure existante)

---

# 🚨 PROBLÈMES CRITIQUES (BLOQUANTS)

## 1️⃣ Authentication Error 401 OpenRouter

### Diagnostic Détaillé
```
Type           : Erreur d'authentification API
Criticité      : CRITIQUE (bloque Agent Zero)
Impact         : Extension "memorize solutions" inopérante
Erreur exacte  : {"error":{"message":"Missing Authentication header","code":401}}
Stack trace    : litellm.exceptions.AuthenticationError: OpenrouterException
Détectée le    : À chaque exécution d'Agent Zero
```

### Analyse Technique
**Cause racine :**
```
1. Agent Zero charge configuration interne (ne lit pas ~/.a0/config.yaml par défaut)
2. Configuration interne inclut : model = "openrouter/..."
3. Agent Zero essaie d'appeler OpenRouter API
4. OPENROUTER_API_KEY vide (par PARAPLUIE patch)
5. OpenRouter refuse requête sans authentification → 401
```

**Chaîne d'exécution problématique :**
```
Agent Zero démarré
  ↓
Charger config (interne, pas custom)
  ↓
Extension "memorize solutions" activée
  ↓
Appel LLM requis
  ↓
Détecte: model = "openrouter/llama2"
  ↓
Cherche OPENROUTER_API_KEY
  ↓
Trouve: "" (vide - PARAPLUIE patch)
  ↓
Appelle OpenRouter sans auth
  ↓
OpenRouter rejette: 401 Unauthorized ❌
```

### Solution Complète

#### Étape 1.1 : Vérifier Absence Actuelle de ~/.a0/config.yaml
```bash
# Vérifier si config personnalisée existe
ls -la ~/.a0/config.yaml 2>/dev/null && echo "✅ Existe" || echo "❌ N'existe pas"

# Vérifier répertoire
ls -la ~/.a0/ 2>/dev/null || echo "Répertoire ~/.a0 n'existe pas"
```

#### Étape 1.2 : Créer Configuration Agent Zero Correcte
```bash
# Créer répertoire
mkdir -p ~/.a0/logs

# Créer config.yaml
cat > ~/.a0/config.yaml << 'EOF'
# Configuration Agent Zero - Mode LLM Local Exclusif
# =====================================================

# Provider principal : Ollama (local)
provider: "ollama"
default_model: "llama3.2:3b"

# Configuration Ollama
ollama:
  enabled: true
  base_url: "http://localhost:8000"
  model: "llama3.2:3b"
  temperature: 0.7
  top_p: 0.9
  top_k: 40
  num_ctx: 4096

# Désactiver OpenRouter COMPLÈTEMENT
openrouter:
  enabled: false
  api_key: ""
  
openai:
  enabled: false
  api_key: ""

# Extensions - Configuration Locale
extensions:
  memorize_solutions:
    enabled: true
    provider: "ollama"
    model: "llama3.2:3b"
    max_memory_items: 50
    
  code_generation:
    enabled: true
    provider: "ollama"
    model: "llama3.2:3b"
    
  summarization:
    enabled: true
    provider: "ollama"
    model: "llama3.2:3b"

# Logging détaillé
logging:
  level: "DEBUG"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "~/.a0/logs/agent_zero.log"
  max_size_mb: 100
  backup_count: 5

# Timeout et performance
performance:
  request_timeout_seconds: 60
  max_concurrent_requests: 3
  enable_caching: true
EOF

# Vérifier le fichier créé
cat ~/.a0/config.yaml
```

#### Étape 1.3 : Créer .env.local avec Vars d'Environnement
```bash
cat > ~/.a0/.env.local << 'EOF'
# Configuration Agent Zero - Variables d'Environnement
# ====================================================

# Mode LLM Local
A0_PROVIDER=ollama
A0_MODEL=llama3.2:3b
A0_OLLAMA_BASE_URL=http://localhost:8000

# Désactiver OpenRouter
A0_OPENROUTER_ENABLED=false
A0_OPENROUTER_API_KEY=""

# Désactiver OpenAI
A0_OPENAI_ENABLED=false
A0_OPENAI_API_KEY=""

# Logging
A0_LOG_LEVEL=DEBUG
A0_LOG_FILE=~/.a0/logs/agent_zero.log

# Extensions
A0_EXTENSIONS_MEMORIZE_SOLUTIONS=enabled
A0_EXTENSIONS_CODE_GENERATION=enabled
A0_EXTENSIONS_SUMMARIZATION=enabled

# Performance
A0_REQUEST_TIMEOUT=60
A0_MAX_CONCURRENT=3

# Désactiver explicitement les clés globales
OPENROUTER_API_KEY=""
OPENAI_API_KEY=""
EOF

# Vérifier le fichier
cat ~/.a0/.env.local
```

#### Étape 1.4 : Mettre à Jour Script de Démarrage Agent Zero
```bash
# Créer script de démarrage sécurisé
cat > ~/.a0/start_agent_zero.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Configuration Agent Zero - Mode Local"
echo "=========================================="

# Charger variables d'environnement
export $(cat ~/.a0/.env.local | xargs)

# Vérifier Ollama accessible
echo "✓ Vérification Ollama..."
OLLAMA_RESPONSE=$(curl -s -X GET http://localhost:8000/api/tags)
if [[ $OLLAMA_RESPONSE == *"models"* ]]; then
    echo "✅ Ollama accessible"
else
    echo "❌ Ollama non accessible sur http://localhost:8000"
    echo "   Démarrer Ollama : docker run -d --gpus=all -p 11434:11434 -p 8000:11434 ollama/ollama"
    exit 1
fi

# Vérifier modèle disponible
echo "✓ Vérification modèle llama3.2:3b..."
if docker exec -it ollama ollama list | grep -q "llama3.2:3b"; then
    echo "✅ Modèle disponible"
else
    echo "❌ Modèle llama3.2:3b non trouvé"
    echo "   Télécharger : docker exec -it ollama ollama pull llama3.2:3b"
    exit 1
fi

# Démarrer Agent Zero
echo "🚀 Démarrage Agent Zero..."
cd /chemin/vers/agent-zero
python main.py --config ~/.a0/config.yaml

EOF

chmod +x ~/.a0/start_agent_zero.sh
```

#### Étape 1.5 : Vérifier Configuration Chargée au Démarrage
```bash
# Ajouter au démarrage d'Agent Zero une vérification
# Ajouter cette ligne au début de main.py ou equivalent:

cat > ~/.a0/verify_config.py << 'EOF'
#!/usr/bin/env python3
import os
import yaml

def verify_agent_zero_config():
    """Vérifier que la configuration est correctement chargée"""
    
    config_file = os.path.expanduser("~/.a0/config.yaml")
    
    print("📋 Vérification Configuration Agent Zero")
    print("=" * 50)
    
    # Vérifier existence fichier config
    if not os.path.exists(config_file):
        print("❌ ERREUR: ~/.a0/config.yaml n'existe pas")
        return False
    
    # Charger config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Vérifications critiques
    checks = [
        ("Provider", config.get('provider') == 'ollama', f"Attendu: ollama, Obtenu: {config.get('provider')}"),
        ("OpenRouter Désactivé", config.get('openrouter', {}).get('enabled') == False, "OpenRouter doit être disabled"),
        ("OpenRouter API Key Vide", config.get('openrouter', {}).get('api_key') == '', "API key doit être vide"),
        ("Ollama Base URL", config.get('ollama', {}).get('base_url') == 'http://localhost:8000', "URL Ollama incorrecte"),
        ("Extension memorize_solutions", config.get('extensions', {}).get('memorize_solutions', {}).get('enabled') == True, "Extension doit être activée"),
    ]
    
    all_ok = True
    for check_name, check_result, error_msg in checks:
        status = "✅" if check_result else "❌"
        print(f"{status} {check_name}: {error_msg if not check_result else 'OK'}")
        if not check_result:
            all_ok = False
    
    print("=" * 50)
    if all_ok:
        print("✅ Configuration VALIDE - Agent Zero peut démarrer")
        return True
    else:
        print("❌ Configuration INVALIDE - Corriger avant de démarrer")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if verify_agent_zero_config() else 1)

EOF

# Exécuter vérification
python3 ~/.a0/verify_config.py
```

### Validation de la Solution
```bash
# Après toutes les étapes ci-dessus, vérifier:

# 1. Config présente
ls -l ~/.a0/config.yaml

# 2. Config contient bonnes valeurs
grep -A 2 "provider:" ~/.a0/config.yaml
grep -A 2 "openrouter:" ~/.a0/config.yaml

# 3. Env vars correctes
source ~/.a0/.env.local
echo "Provider: $A0_PROVIDER"
echo "OpenRouter Enabled: $A0_OPENROUTER_ENABLED"
echo "OpenRouter API Key: $A0_OPENROUTER_API_KEY"

# 4. Aucune clé API visible
grep -i "sk-\|openrouter-" ~/.a0/config.yaml ~/.a0/.env.local || echo "✅ Aucune clé API exposée"

# 5. Test avec curl
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Test"}],
    "stream": false
  }'
```

### Prévention Future
```bash
# Ajouter ces vérifications au hook pre-commit/pre-push:
# (empêcher de committer des clés API)

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Vérifier que pas de clés API en dur
if git diff --cached | grep -E "sk-|openrouter-|OPENROUTER_API_KEY.*=.*[^ ]"; then
    echo "❌ ERREUR: Clé API détectée dans commit"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

---

## 2️⃣ Configuration Agent Zero Manquante

### Diagnostic Détaillé
```
Type           : Fichier de configuration absent
Criticité      : CRITIQUE (bloque démarrage correct)
Impact         : Agent Zero utilise config par défaut (OpenRouter)
Emplacement    : ~/.a0/config.yaml
Statut         : PARTIELLEMENT RÉSOLU (config créée mais non testée)
```

### Analyse Technique
**Agent Zero recherche configuration dans cet ordre :**
```
1. ~/.a0/config.yaml (PRIORITÉ 1 - N'existe pas)
   ↓ (pas trouvé)
2. /etc/a0/config.yaml (PRIORITÉ 2 - N'existe pas)
   ↓ (pas trouvé)
3. ./config.yaml (PRIORITÉ 3 - N'existe pas)
   ↓ (pas trouvé)
4. Config par défaut interne (PRIORITÉ 4 - ✅ UTILISE)
   → Inclut: "model": "openrouter/llama2"
   → Inclut: "provider": "openrouter"
   → Inclut: chercher OPENROUTER_API_KEY
   ↓
❌ Configuration interne par défaut lance OpenRouter
```

### Solution Complète
**➡️ Voir Solution du Problème #1 ci-dessus (Étapes 1.2-1.5)**

Cette solution crée exactement ~/.a0/config.yaml requis.

### Vérification Post-Déploiement
```bash
# Confirmer config est lue au démarrage
tail -50 ~/.a0/logs/agent_zero.log | grep -i "config\|provider\|openrouter"

# Résultat attendu:
# [INFO] Loading configuration from ~/.a0/config.yaml
# [INFO] Provider: ollama
# [INFO] OpenRouter: DISABLED
# [INFO] Extension 'memorize_solutions' loaded
```

---

## 3️⃣ Ollama Non Démarré

### Diagnostic Détaillé
```
Type           : Service Docker non lancé
Criticité      : CRITIQUE (aucun LLM local disponible)
Impact         : Pas d'alternative à OpenRouter
Service        : Conteneur Docker ollama/ollama
Ports requis   : 11434 (natif) et 8000 (alternative)
État actuel    : ❌ NON LANCÉ
```

### Vérification d'Absence
```bash
# Vérifier si container Ollama tourne
docker ps | grep ollama
# Résultat attendu si absent: (aucune ligne)

# Vérifier si container existe mais arrêté
docker ps -a | grep ollama
# Résultat: soit absent soit state "Exited"

# Vérifier si ports libres
netstat -tulpn 2>/dev/null | grep -E "11434|8000" || echo "✅ Ports libres"
```

### Solution Complète

#### Étape 3.1 : Démarrer Ollama Container
```bash
# Commande de démarrage complète
docker run -d \
    --gpus=all \
    -v "${PWD}/ollama:/root/.ollama" \
    -p 11434:11434 \
    -p 8000:11434 \
    --restart unless-stopped \
    --name ollama \
    ollama/ollama

# Explication des flags:
# -d                                    : Exécuter en background
# --gpus=all                            : Utiliser tous les GPUs NVIDIA disponibles
# -v "${PWD}/ollama:/root/.ollama"     : Persister les modèles sur disque local
# -p 11434:11434                        : Mapper port Ollama natif
# -p 8000:11434                         : Mapper port alternatif (compatibilité API)
# --restart unless-stopped              : Redémarrer auto si crash
# --name ollama                         : Nommer le container
# ollama/ollama                         : Image Docker officielle
```

#### Étape 3.2 : Vérifier Démarrage Réussi
```bash
# Attendre quelques secondes (initialisation)
sleep 5

# Vérifier container actif
docker ps | grep ollama
# Résultat attendu:
# ollama  ollama/ollama  "..."  Up 3 seconds (sain)

# Vérifier logs sans erreur
docker logs ollama | tail -20
# Résultat attendu: pas d'erreur, message prêt

# Vérifier santé container
docker inspect ollama --format='{{.State.Status}}'
# Résultat attendu: "running"
```

#### Étape 3.3 : Tester Connectivité API Ollama
```bash
# Test 1 : Vérifier API répondent
curl -s http://localhost:11434/api/tags | jq .
# Résultat attendu: JSON avec clé "models": []

curl -s http://localhost:8000/api/tags | jq .
# Résultat attendu: même JSON

# Test 2 : Vérifier ports accessibles
echo "Test port 11434:" && nc -zv localhost 11434
echo "Test port 8000:" && nc -zv localhost 8000
# Résultat attendu: "Connection succeeded"
```

#### Étape 3.4 : Télécharger Modèles LLM
```bash
# Modèle principal
docker exec -it ollama ollama pull llama3.2:3b
# Temps: ~5-10 minutes selon débit Internet
# Taille: ~2GB

# Modèles alternatifs
docker exec -it ollama ollama pull phi3.5:3.8b
# Temps: ~3-5 minutes
# Taille: ~2.3GB

docker exec -it ollama ollama pull gemma2:2b
# Temps: ~2-3 minutes
# Taille: ~1.4GB

# Progress indicator:
# Pulling llama3.2:3b
# [===>                ] 234 MB / 2.0 GB
```

#### Étape 3.5 : Vérifier Modèles Disponibles
```bash
# Lister modèles téléchargés
docker exec ollama ollama list
# Résultat attendu:
# NAME              ID              SIZE      MODIFIED
# llama3.2:3b       a80c4f17acd5    2.0 GB    2 minutes ago
# phi3.5:3.8b       4169cdfa9d85    2.3 GB    30 seconds ago
# gemma2:2b         4047dc3b73bb    1.4 GB    15 seconds ago

# Vérifier taille totale disque
docker exec ollama du -sh /root/.ollama
# Résultat attendu: ~5.7 GB (3 modèles)
```

#### Étape 3.6 : Test API Complète Avec Modèle
```bash
# Test requête API complète
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "user", "content": "Quel est 2+2?"}
    ],
    "stream": false,
    "temperature": 0.7
  }'

# Résultat attendu:
# {
#   "model": "llama3.2:3b",
#   "created": 1234567890,
#   "choices": [
#     {
#       "message": {
#         "role": "assistant",
#         "content": "2+2 égale 4."
#       }
#     }
#   ]
# }
```

#### Étape 3.7 : Configurer Auto-Redémarrage
```bash
# Vérifier container redémarre après crash
docker update --restart unless-stopped ollama

# Tester redémarrage auto
docker stop ollama
sleep 2
docker ps | grep ollama
# Résultat attendu: container redémarré automatiquement
```

#### Étape 3.8 : Monitoring Continu (Optionnel mais Recommandé)
```bash
# Créer script monitoring
cat > ~/.a0/monitor_ollama.sh << 'EOF'
#!/bin/bash
echo "📊 Monitoring Ollama"
echo "===================="

while true; do
    clear
    echo "⏰ $(date '+%H:%M:%S')"
    echo ""
    
    # CPU/RAM usage
    echo "📈 Ressources:"
    docker stats ollama --no-stream --format "table {{.MemUsage}}\t{{.CPUPerc}}"
    
    # Modèles disponibles
    echo ""
    echo "🤖 Modèles:"
    docker exec ollama ollama list
    
    # Test rapide API
    echo ""
    echo "🔌 API Status:"
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" http://localhost:8000/api/tags)
    STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
    echo "HTTP Status: $STATUS"
    [[ $STATUS == "200" ]] && echo "✅ API OK" || echo "❌ API KO"
    
    sleep 5
done
EOF

chmod +x ~/.a0/monitor_ollama.sh

# Lancer monitoring en arrière-plan
nohup ~/.a0/monitor_ollama.sh > ~/.a0/logs/ollama_monitor.log 2>&1 &
```

### Checklist Complète Ollama
```bash
# ✅ Avant de continuer, tous ces tests doivent passer:

# 1. Container tourne
docker ps | grep ollama | grep -q "Up" && echo "✅ Container actif" || echo "❌ FAIL"

# 2. Ports accessibles
nc -zv localhost 11434 2>&1 | grep -q "succeeded" && echo "✅ Port 11434 OK" || echo "❌ FAIL"
nc -zv localhost 8000 2>&1 | grep -q "succeeded" && echo "✅ Port 8000 OK" || echo "❌ FAIL"

# 3. Modèles présents
docker exec ollama ollama list | grep -q "llama3.2:3b" && echo "✅ Modèle OK" || echo "❌ FAIL"

# 4. API répond
curl -s http://localhost:8000/api/tags | jq . > /dev/null && echo "✅ API OK" || echo "❌ FAIL"

# 5. Modèle répond
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.2:3b","messages":[{"role":"user","content":"test"}],"stream":false}' \
  | jq . > /dev/null && echo "✅ LLM Répond" || echo "❌ FAIL"
```

---

# ⚠️ PROBLÈMES MINEURS (GÊNANTS)

## 4️⃣ Variables d'Environnement Non Héritées

### Diagnostic Détaillé
```
Type           : Isolation des processus
Criticité      : MOYEN (contournable)
Impact         : Agent Zero ne voit pas variables système
Variables      : OPENROUTER_API_KEY, OPENAI_API_KEY, etc.
Cause          : Processus enfant n'hérite pas env du parent
```

### Explication Technique
```
Situation:
  Terminal (env vars chargés)
    ↓
  Démarrage Agent Zero
    ↓
  Processus enfant Agent Zero (NEW env isolated)
    ↓
  Agent Zero ne voit que ses env variables propres
  ↓
❌ OPENROUTER_API_KEY vide même si défini dans Terminal
```

### Solution Complète

#### Étape 4.1 : Vérifier Variables Actuelles
```bash
# Afficher variables visibles au processus courant
echo "Variables en mémoire:"
env | grep -i "openrouter\|openai\|a0_"

# Créer fichier de diagnostic
cat > ~/.a0/check_env.sh << 'EOF'
#!/bin/bash
echo "📋 Variables d'Environnement - Diagnostic"
echo "========================================="

# Variables actuelles du shell
echo ""
echo "🔷 Variables Shell Courant:"
env | grep -i "openrouter\|openai\|a0_" || echo "  (aucune)"

# Variables espérées
echo ""
echo "🔷 Variables Requises pour Agent Zero:"
echo "  A0_PROVIDER (attendu: ollama)"
echo "  A0_MODEL (attendu: llama3.2:3b)"
echo "  A0_OLLAMA_BASE_URL (attendu: http://localhost:8000)"
echo "  A0_OPENROUTER_ENABLED (attendu: false)"

# Variables fichier .env.local
echo ""
echo "🔷 Variables dans ~/.a0/.env.local:"
if [ -f ~/.a0/.env.local ]; then
    cat ~/.a0/.env.local | grep -v "^#" | grep -v "^$"
else
    echo "  (fichier n'existe pas)"
fi

EOF

chmod +x ~/.a0/check_env.sh
bash ~/.a0/check_env.sh
```

#### Étape 4.2 : Sourcer .env.local Avant Démarrage
```bash
# Méthode 1 : Dans Terminal avant démarrage Agent Zero
source ~/.a0/.env.local
echo "✅ Variables chargées"

# Vérifier chargement
echo "Provider: $A0_PROVIDER"
echo "Model: $A0_MODEL"

# Puis démarrer Agent Zero
python main.py --config ~/.a0/config.yaml
```

#### Étape 4.3 : Créer Script Démarrage Automatisé
```bash
# Créer launcher qui gère variables automatiquement
cat > ~/.a0/run_agent_zero.sh << 'EOF'
#!/bin/bash
set -e

# Charger variables d'environnement
echo "📦 Chargement variables d'environnement..."
if [ -f ~/.a0/.env.local ]; then
    export $(cat ~/.a0/.env.local | xargs)
    echo "✅ Variables chargées de ~/.a0/.env.local"
else
    echo "❌ Fichier ~/.a0/.env.local manquant"
    exit 1
fi

# Afficher configuration chargée
echo ""
echo "📋 Configuration Active:"
echo "  Provider: $A0_PROVIDER"
echo "  Model: $A0_MODEL"
echo "  Ollama URL: $A0_OLLAMA_BASE_URL"
echo "  OpenRouter Enabled: $A0_OPENROUTER_ENABLED"
echo ""

# Vérifier Ollama accessible
echo "🔍 Vérification Infrastructure..."
if ! curl -s http://localhost:8000/api/tags > /dev/null; then
    echo "❌ Ollama non accessible"
    echo "   Démarrer: docker run -d --gpus=all -p 8000:11434 ollama/ollama"
    exit 1
fi
echo "✅ Ollama accessible"

# Démarrer Agent Zero
echo ""
echo "🚀 Démarrage Agent Zero..."
cd /chemin/vers/agent-zero
python main.py --config ~/.a0/config.yaml

EOF

chmod +x ~/.a0/run_agent_zero.sh

# Utiliser ce script pour lancer Agent Zero à la place
~/.a0/run_agent_zero.sh
```

#### Étape 4.4 : Configurer Variables Globales Système (Linux/Mac)
```bash
# Pour rendre variables permanentes au système

# Option 1 : .bashrc / .zshrc
cat >> ~/.bashrc << 'EOF'
# Agent Zero Environment
if [ -f ~/.a0/.env.local ]; then
    export $(cat ~/.a0/.env.local | xargs)
fi
EOF

# Option 2 : /etc/environment (tous les utilisateurs)
sudo tee -a /etc/environment << 'EOF'
A0_PROVIDER=ollama
A0_MODEL=llama3.2:3b
A0_OLLAMA_BASE_URL=http://localhost:8000
A0_OPENROUTER_ENABLED=false
EOF

# Recharger shell
exec $SHELL
```

#### Étape 4.5 : Vérifier Variables en Processus Enfant
```bash
# Tester que processus enfant voit variables
cat > ~/.a0/test_env_inheritance.sh << 'EOF'
#!/bin/bash

export TEST_VAR="valeur_parent"

# Créer processus enfant qui affiche variable
python3 << 'PYTHON'
import os
print("Variable dans enfant:", os.getenv("TEST_VAR", "NON TROUVÉ"))
PYTHON

EOF

chmod +x ~/.a0/test_env_inheritance.sh
bash ~/.a0/test_env_inheritance.sh
# Résultat attendu: "valeur_parent" (transmission OK)
```

---

## 5️⃣ Conflit PARAPLUIE Patch

### Diagnostic Détaillé
```
Type           : Configuration contradictoire
Criticité      : MOYEN (par design pour forcer local)
Impact         : PARAPLUIE vide OPENROUTER_API_KEY intentionnellement
Fichier        : parapluie_patch.py
Ligne          : os.environ["OPENROUTER_API_KEY"] = ""
Problème       : Agent Zero essaie quand même d'utiliser OpenRouter
```

### Analyse Technique
```
Intention PARAPLUIE:
  Vider OPENROUTER_API_KEY
  → Force utilisation mode local
  → Prévient fuite API key en cas de bug

Réalité:
  Agent Zero utilise config interne par défaut
  → Config interne dit "utiliser openrouter"
  → Essaie de appeler OpenRouter même si clé vide
  ↓
❌ Conflit: PARAPLUIE vide clé, mais config dit utiliser le service
```

### Solution Complète

#### Étape 5.1 : Désactiver Complètement PARAPLUIE (Option Recommandée)
```bash
# Vérifier si PARAPLUIE existe et son contenu
find . -name "parapluie_patch.py" -o -name "*parapluie*" 2>/dev/null

# Sauvegarder original
cp parapluie_patch.py parapluie_patch.py.backup

# Créer version qui désactive OpenRouter complètement
cat > parapluie_patch.py << 'EOF'
"""
PARAPLUIE Patch - Mode Local Exclusif
Force Agent Zero à utiliser Ollama local, désactive complètement OpenRouter
"""

import os
import json
from pathlib import Path

def patch_agent_zero_config():
    """Configurer Agent Zero pour mode local uniquement"""
    
    # Désactiver tous les services externes
    os.environ["OPENROUTER_ENABLED"] = "false"
    os.environ["OPENROUTER_API_KEY"] = ""
    os.environ["OPENAI_ENABLED"] = "false"
    os.environ["OPENAI_API_KEY"] = ""
    
    # Forcer provider local
    os.environ["A0_PROVIDER"] = "ollama"
    os.environ["A0_MODEL"] = "llama3.2:3b"
    os.environ["A0_OLLAMA_BASE_URL"] = "http://localhost:8000"
    
    # Charger config custom si existe
    config_path = Path.home() / ".a0" / "config.yaml"
    if config_path.exists():
        print(f"[PARAPLUIE] Utilisant config custom: {config_path}")
    else:
        print(f"[PARAPLUIE] Config custom manquante: {config_path}")
        print("[PARAPLUIE] Créer avec: mkdir -p ~/.a0 && cat > ~/.a0/config.yaml << EOF...")
    
    print("[PARAPLUIE] Configuration Mode Local:")
    print(f"  Provider: {os.environ.get('A0_PROVIDER')}")
    print(f"  Model: {os.environ.get('A0_MODEL')}")
    print(f"  Ollama URL: {os.environ.get('A0_OLLAMA_BASE_URL')}")
    print(f"  OpenRouter: DISABLED")
    print("[PARAPLUIE] Patch appliqué ✅")

if __name__ == '__main__':
    patch_agent_zero_config()

EOF

# Appeler patch au démarrage
python parapluie_patch.py
```

#### Étape 5.2 : Intégrer PARAPLUIE au Démarrage Agent Zero
```bash
# Modifier main.py ou équivalent pour appeler patch AVANT tout

# Ajouter au début de main.py:
cat >> main.py.patch << 'EOF'
# Au début du fichier, AVANT import agent_zero:
import sys
sys.path.insert(0, os.path.dirname(__file__))
import parapluie_patch
parapluie_patch.patch_agent_zero_config()

EOF

# Ou créer wrapper:
cat > run_agent_zero_with_patch.py << 'EOF'
#!/usr/bin/env python3
import os
import sys

# Appliquer patch AVANT tout
import parapluie_patch
parapluie_patch.patch_agent_zero_config()

# Puis lancer Agent Zero
os.chdir('/chemin/vers/agent-zero')
exec(open('main.py').read())

EOF
```

#### Étape 5.3 : Vérifier Patch Effectif
```bash
# Vérifier que patch est appliqué
cat > ~/.a0/verify_patch.py << 'EOF'
#!/usr/bin/env python3
import os

print("📋 Vérification Patch PARAPLUIE")
print("=" * 50)

checks = [
    ("OpenRouter Disabled", os.getenv("OPENROUTER_ENABLED", "").lower() == "false"),
    ("OpenRouter API Key Empty", os.getenv("OPENROUTER_API_KEY", "") == ""),
    ("Provider = ollama", os.getenv("A0_PROVIDER", "") == "ollama"),
    ("Model = llama3.2:3b", os.getenv("A0_MODEL", "") == "llama3.2:3b"),
    ("Ollama URL OK", os.getenv("A0_OLLAMA_BASE_URL", "") == "http://localhost:8000"),
]

all_ok = True
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if not result:
        all_ok = False

print("=" * 50)
if all_ok:
    print("✅ Patch valide - Agent Zero peut démarrer")
else:
    print("❌ Patch incomplet - Vérifier configuration")

EOF

python3 ~/.a0/verify_patch.py
```

---

## 6️⃣ Scripts PowerShell avec Erreurs de Syntaxe

### Diagnostic Détaillé
```
Type           : Erreurs d'échappement de caractères
Criticité      : MOYEN (blocks automation)
Fichiers       : STOP_ERROR_NOW.ps1, URGENT_FIX_NOW.ps1
Impact         : Scripts d'automatisation ne s'exécutent pas
Erreur         : Caractères Unicode mal interprétés
```

### Identification des Scripts Problématiques
```bash
# Trouver tous les fichiers PowerShell
find . -name "*.ps1" -type f

# Vérifier encoding
file *.ps1
# Résultat peut montrer: "UTF-8 with BOM" ou caractères spéciaux

# Rechercher caractères problématiques
grep -P -n '[\x80-\xFF]' *.ps1 | head -10
```

### Solution Complète

#### Étape 6.1 : Corriger STOP_ERROR_NOW.ps1
```bash
# Sauvegarder original
cp STOP_ERROR_NOW.ps1 STOP_ERROR_NOW.ps1.backup

# Créer version corrigée (texte ASCII pur)
cat > STOP_ERROR_NOW.ps1 << 'EOF'
# STOP_ERROR_NOW.ps1 - Correction erreur 401 OpenRouter
# Script PowerShell pour arrêter Agent Zero et nettoyer configuration

param(
    [switch]$Force = $false
)

Write-Host "======================================" -ForegroundColor Yellow
Write-Host "STOP ERREUR 401 - Agent Zero" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Yellow

# 1. Arrêter Agent Zero
Write-Host "[1/4] Arret Agent Zero..." -ForegroundColor Cyan
$process = Get-Process -Name "*agent*zero*" -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -InputObject $process -Force:$Force
    Write-Host "  ARRETE" -ForegroundColor Green
} else {
    Write-Host "  Pas en execution" -ForegroundColor Gray
}

# 2. Vérifier Ollama
Write-Host "[2/4] Verification Ollama..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/tags" -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  OK" -ForegroundColor Green
    }
} catch {
    Write-Host "  Ollama non accessible - Demarrer avec:" -ForegroundColor Yellow
    Write-Host "  docker run -d --gpus=all -p 8000:11434 ollama/ollama"
}

# 3. Nettoyer variables d'environnement
Write-Host "[3/4] Nettoyage variables..." -ForegroundColor Cyan
$env:OPENROUTER_API_KEY = ""
$env:OPENAI_API_KEY = ""
$env:A0_PROVIDER = "ollama"
$env:A0_MODEL = "llama3.2:3b"
Write-Host "  NETTOYE" -ForegroundColor Green

# 4. Afficher configuration
Write-Host "[4/4] Configuration:" -ForegroundColor Cyan
Write-Host "  Provider: $($env:A0_PROVIDER)"
Write-Host "  Model: $($env:A0_MODEL)"
Write-Host "  Ollama URL: $($env:A0_OLLAMA_BASE_URL)"
Write-Host "  OpenRouter: DISABLED"

Write-Host ""
Write-Host "========== PRÊT POUR RELANCER ==========" -ForegroundColor Green

EOF

# Vérifier syntax
powershell -NoProfile -Command {
    try {
        [scriptblock]::Create((Get-Content STOP_ERROR_NOW.ps1 -Raw))
        Write-Host "Syntax valide"
    } catch {
        Write-Host "Erreur syntax: $_"
    }
}
```

#### Étape 6.2 : Corriger URGENT_FIX_NOW.ps1
```bash
# Sauvegarder original
cp URGENT_FIX_NOW.ps1 URGENT_FIX_NOW.ps1.backup

# Créer version corrigée
cat > URGENT_FIX_NOW.ps1 << 'EOF'
# URGENT_FIX_NOW.ps1 - Fix 401 OpenRouter Error
# Script automatise pour configurer Agent Zero mode local

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "URGENT FIX - Erreur 401 OpenRouter" -ForegroundColor Red
Write-Host "===============================================" -ForegroundColor Cyan

# Detecter OS
$IsLinux = $PSVersionTable.OS -like "*linux*"
$IsMac = $PSVersionTable.OS -like "*darwin*"
$IsWindows = $PSVersionTable.Platform -eq "Win32NT"

# Déterminer home directory
if ($IsLinux -or $IsMac) {
    $HomeDir = $env:HOME
} else {
    $HomeDir = $env:USERPROFILE
}

$ConfigDir = Join-Path $HomeDir ".a0"
$ConfigFile = Join-Path $ConfigDir "config.yaml"
$EnvFile = Join-Path $ConfigDir ".env.local"
$LogDir = Join-Path $ConfigDir "logs"

Write-Host ""
Write-Host "Plateforme: $(if ($IsLinux) {'Linux'} elseif ($IsMac) {'macOS'} else {'Windows'})" -ForegroundColor Yellow
Write-Host "Home: $HomeDir" -ForegroundColor Yellow

# Créer répertoire .a0
Write-Host ""
Write-Host "[ETAPE 1] Creation repertoire .a0..." -ForegroundColor Cyan
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    Write-Host "  CREE" -ForegroundColor Green
} else {
    Write-Host "  EXISTE" -ForegroundColor Green
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Créer config.yaml
Write-Host ""
Write-Host "[ETAPE 2] Creation config.yaml..." -ForegroundColor Cyan

$configContent = @"
# Configuration Agent Zero - Mode LLM Local Exclusif
provider: "ollama"
default_model: "llama3.2:3b"

ollama:
  enabled: true
  base_url: "http://localhost:8000"
  model: "llama3.2:3b"
  temperature: 0.7
  top_p: 0.9
  top_k: 40

openrouter:
  enabled: false
  api_key: ""
  
openai:
  enabled: false
  api_key: ""

extensions:
  memorize_solutions:
    enabled: true
    provider: "ollama"
    model: "llama3.2:3b"

logging:
  level: "DEBUG"
  file: "~/.a0/logs/agent_zero.log"
"@

Set-Content -Path $ConfigFile -Value $configContent -Encoding UTF8
Write-Host "  ECRIT: $ConfigFile" -ForegroundColor Green

# Créer .env.local
Write-Host ""
Write-Host "[ETAPE 3] Creation .env.local..." -ForegroundColor Cyan

$envContent = @"
A0_PROVIDER=ollama
A0_MODEL=llama3.2:3b
A0_OLLAMA_BASE_URL=http://localhost:8000
A0_OPENROUTER_ENABLED=false
A0_OPENROUTER_API_KEY=
OPENROUTER_API_KEY=
OPENAI_API_KEY=
"@

Set-Content -Path $EnvFile -Value $envContent -Encoding UTF8
Write-Host "  ECRIT: $EnvFile" -ForegroundColor Green

# Tester Ollama
Write-Host ""
Write-Host "[ETAPE 4] Verification Ollama..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/tags" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ACCESSIBLE" -ForegroundColor Green
    
    # Vérifier modèles
    $models = $response.Content | ConvertFrom-Json
    if ($models.models.Count -gt 0) {
        Write-Host "  Modeles disponibles:" -ForegroundColor Green
        foreach ($model in $models.models) {
            Write-Host "    - $($model.name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ATTENTION: Aucun modele. Telecharger: docker exec ollama ollama pull llama3.2:3b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ERREUR: Ollama non accessible" -ForegroundColor Red
    Write-Host "  Demarrer avec: docker run -d --gpus=all -p 8000:11434 ollama/ollama" -ForegroundColor Yellow
}

# Résumé
Write-Host ""
Write-Host "=============== CONFIGURATION COMPLETE ===============" -ForegroundColor Green
Write-Host "Config: $ConfigFile"
Write-Host "Env   : $EnvFile"
Write-Host "Logs  : $LogDir"
Write-Host ""
Write-Host "Prochaine etape: Redemarrer Agent Zero" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Green

EOF

# Vérifier syntax
powershell -NoProfile -Command {
    try {
        [scriptblock]::Create((Get-Content URGENT_FIX_NOW.ps1 -Raw))
        Write-Host "✅ Syntaxe valide"
    } catch {
        Write-Host "❌ Erreur: $_"
    }
}
```

#### Étape 6.3 : Vérifier Encoding Fichiers
```bash
# Vérifier encoding
file *.ps1

# Si "UTF-8 with BOM", convertir en UTF-8 simple
for file in *.ps1; do
    iconv -f UTF-8 -t UTF-8 "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done

# Vérifier caractères spéciaux
od -c *.ps1 | grep -E "\\377|\\376|[^[:print:]]" || echo "✅ ASCII valide"
```

#### Étape 6.4 : Tester Exécution Scripts
```powershell
# Exécuter test de syntax
powershell -NoProfile -ExecutionPolicy Bypass -File STOP_ERROR_NOW.ps1 -WhatIf

# Exécuter fix script complet
powershell -NoProfile -ExecutionPolicy Bypass -File URGENT_FIX_NOW.ps1
```

---

# 🔍 PROBLÈMES LATENTS (POTENTIELS)

## 7️⃣ Dépendance GPU Non Vérifiée

### Diagnostic Détaillé
```
Type           : Infrastructure manquante (optionnelle mais recommandée)
Criticité      : BAS (fonctionne en CPU-only, mais lent)
Impact         : Ollama très lent sans GPU NVIDIA
Vérification   : nvidia-smi
Alternative    : Mode CPU-only (5-10x plus lent)
```

### Solution Complète

#### Étape 7.1 : Vérifier GPU NVIDIA Disponible
```bash
# Vérifier si nvidia-smi installé
which nvidia-smi
# Résultat: /usr/bin/nvidia-smi ou absence

# Afficher infos GPU
nvidia-smi
# Résultat: liste des GPUs disponibles

# Vérifier CUDA installé
nvcc --version
# Résultat: version CUDA (ex: release 11.8)

# Vérifier cuDNN installé
find /usr/local/cuda -name "cudnn*" 2>/dev/null | head -5

# Vérifier Docker GPU access
docker run --rm --gpus all ubuntu nvidia-smi
# Résultat: GPU visible dans container
```

#### Étape 7.2 : Configurer Docker pour GPU
```bash
# Installer NVIDIA Container Runtime
# Ubuntu/Debian:
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-runtime

# Redémarrer Docker
sudo systemctl restart docker

# Tester accès GPU
docker run --rm --gpus all ubuntu nvidia-smi
```

#### Étape 7.3 : Démarrer Ollama avec GPU Support
```bash
# Avec GPU (recommandé)
docker run -d \
    --gpus=all \
    -v "${PWD}/ollama:/root/.ollama" \
    -p 11434:11434 \
    -p 8000:11434 \
    ollama/ollama

# Sans GPU (mode CPU-only, très lent)
docker run -d \
    -v "${PWD}/ollama:/root/.ollama" \
    -p 11434:11434 \
    -p 8000:11434 \
    ollama/ollama

# Vérifier GPU utilisé
docker exec ollama nvidia-smi
# Résultat: GPU info ou erreur "no GPU"

# Alternative: vérifier logs
docker logs ollama | grep -i "gpu\|cuda"
```

#### Étape 7.4 : Benchmark Performance
```bash
# Tester vitesse sans GPU (attendu: LENT)
time curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Ecris 10 mots en anglais"}],
    "stream": false
  }' | jq .

# Résultat temps:
# - Avec GPU: 2-5 secondes
# - CPU-only: 30-120 secondes
# - Très lent: >120 secondes = problème config
```

#### Étape 7.5 : Monitorer Utilisation GPU
```bash
# Monitoring en temps réel
watch -n 1 nvidia-smi

# Dans container Ollama
docker exec -it ollama nvidia-smi

# Métriques détaillées
nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.free --format=csv,nounits --loop=1

# Si GPU non utilisé:
# 1. Vérifier --gpus=all dans docker run
# 2. Vérifier nvidia-container-runtime installé
# 3. Vérifier logs: docker logs ollama | grep -i error
# 4. Redémarrer Docker: sudo systemctl restart docker
```

---

## 8️⃣ Modèles LLM Non Téléchargés

### Diagnostic Détaillé
```
Type           : Données manquantes
Criticité      : BAS (découvert rapidement à usage)
Impact         : Ollama démarre mais aucun modèle disponible
Modèles        : llama3.2:3b (minimum), phi3.5:3.8b, gemma2:2b
Espace disque  : ~2GB par modèle, ~5.7GB total 3 modèles
Temps           : ~20-30 minutes download
```

### Solution Complète

#### Étape 8.1 : Vérifier Modèles Actuels
```bash
# Lister modèles disponibles
docker exec ollama ollama list
# Résultat: TABLE avec NAME, ID, SIZE, MODIFIED

# Vérifier espace disque utilisé
docker exec ollama du -sh /root/.ollama
# Résultat: Total size (ex: 2.1G)

# Vérifier espace disque libre
docker exec ollama df -h /root/.ollama
# Résultat: Available space (besoin min 10-20GB)
```

#### Étape 8.2 : Télécharger Modèles
```bash
# Modèle principal - OBLIGATOIRE
docker exec -it ollama ollama pull llama3.2:3b
# Temps: ~10 minutes
# Taille: ~2.0 GB

# Modèles alternatifs - OPTIONNELS
docker exec -it ollama ollama pull phi3.5:3.8b
# Temps: ~5 minutes
# Taille: ~2.3 GB

docker exec -it ollama ollama pull gemma2:2b
# Temps: ~3 minutes
# Taille: ~1.4 GB
```

#### Étape 8.3 : Optimiser Stockage (Optionnel)
```bash
# Garder seulement modèles requis
docker exec -it ollama ollama rm phi3.5:3.8b  # Supprimer si besoin d'espace

# Compresser ollama directory
tar -czf ollama_backup.tar.gz ollama/

# Nettoyer images non utilisées
docker image prune -a
```

---

## 9️⃣ Ports Network Potentiellement Occupés

### Diagnostic Détaillé
```
Type           : Conflit de ports
Criticité      : BAS (rare mais bloquant si présent)
Impact         : Ollama container ne démarre pas
Ports vérifiés : 11434 (natif), 8000 (API)
Symptôme       : "port already in use"
```

### Solution Complète

#### Étape 9.1 : Vérifier Ports Disponibles
```bash
# Linux/Mac
netstat -tuln | grep -E "11434|8000"
# Résultat: aucune ligne = ports libres

# Windows
netstat -ano | findstr /R "11434 8000"
# Résultat: aucune ligne = ports libres

# Alternative universal
ss -tuln | grep -E "11434|8000"
```

#### Étape 9.2 : Trouver Processus Occupant Ports
```bash
# Linux/Mac
lsof -i :11434
lsof -i :8000
# Résultat: processus occupant port

# Windows
netstat -ano | findstr :11434
# Puis identifier PID
tasklist | findstr PID

# Arrêter processus occupant
sudo kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

#### Étape 9.3 : Démarrer Ollama avec Ports Alternatifs
```bash
# Si ports 11434/8000 occupés, utiliser ports différents
docker run -d \
    --gpus=all \
    -v "${PWD}/ollama:/root/.ollama" \
    -p 11435:11434 \
    -p 8001:11434 \
    --name ollama \
    ollama/ollama

# Mettre à jour config Agent Zero
cat >> ~/.a0/config.yaml << 'EOF'
ollama:
  base_url: "http://localhost:8001"
EOF

# Tester nouveaux ports
curl http://localhost:8001/api/tags
```

---

# 🏗️ PROBLÈMES ARCHITECTURAUX

## 🔟 Double Configuration LLM

### Diagnostic Détaillé
```
Type           : Architecture redondante/confuse
Criticité      : STRATÉGIQUE (design decision)
Impact         : Confusion entre Gemma 270M (Hermes) et Ollama (Agent Zero)
Systèmes       : Hermes Agent (Gemma) vs Agent Zero (OpenRouter/Ollama)
Recommandation : Unifier vers Ollama pour simplifier
```

### Analyse Technique
```
Situation actuelle:
  Hermes Agent
    ↓ Utilise
    Gemma 270M (local)
  
  Agent Zero
    ↓ Essaie d'utiliser
    OpenRouter → ERREUR 401
    ↓ Devrait utiliser
    Ollama (mais pas configuré)

Résultat:
❌ 2 LLM locaux différents
❌ Confusion de configuration
❌ Complexité de maintenance
```

### Solution Complète

#### Étape 10.1 : Décision Architecture
```
Option A: Garder Gemma 270M SEULEMENT
  ✅ Pros: Léger, rapide, spécialisé
  ❌ Cons: Moins polyvalent, moins performant

Option B: Utiliser Ollama UNIQUEMENT
  ✅ Pros: Modèles plus performants, plus flexible
  ❌ Cons: Plus lourd, plus lent sans GPU

Option C: Hybrid (recommandé)
  ✅ Gemma 270M pour tâches rapides (Hermes)
  ✅ Ollama Llama3.2:3b pour tâches complexes (Agent Zero)
  ❌ 2 services à maintenir

RECOMMANDATION: Option B (Ollama uniquement)
  - Agent Zero + Hermes Agent → Ollama Llama3.2:3b
  - Centralise configuration
  - Unifie debugging
  - Scalable (upgrade facile)
```

#### Étape 10.2 : Migrer Hermes Agent vers Ollama
```bash
# Arrêter Gemma 270M
docker stop hermes-agent

# Modifier config Hermes Agent
cat > hermes_config.yaml << 'EOF'
# Hermes Agent - Mode Ollama Local
provider: "ollama"
model: "llama3.2:3b"

ollama:
  base_url: "http://localhost:8000"
  model: "llama3.2:3b"

logging:
  level: "INFO"
EOF

# Redémarrer Hermes
docker run -d \
  -v $(pwd)/hermes_config.yaml:/app/config.yaml \
  -p 8080:8000 \
  --name hermes-agent \
  hermes-agent:latest
```

#### Étape 10.3 : Unifier Point d'Entrée
```bash
# Créer unification script
cat > ~/.a0/unified_llm_launcher.sh << 'EOF'
#!/bin/bash

# Unified LLM Launcher - Hermes + Agent Zero
echo "🚀 Demarrage Infrastructure IA Unifiée"
echo "======================================"

# 1. Vérifier Ollama
echo "[1/3] Verification Ollama..."
if ! docker ps | grep -q ollama; then
    echo "Demarrage Ollama..."
    docker run -d \
        --gpus=all \
        -v "${PWD}/ollama:/root/.ollama" \
        -p 11434:11434 \
        -p 8000:11434 \
        --name ollama \
        ollama/ollama
    sleep 5
fi

# 2. Démarrer Hermes Agent
echo "[2/3] Demarrage Hermes Agent..."
docker run -d \
  --name hermes-agent \
  -p 8080:8000 \
  hermes-agent:latest

# 3. Démarrer Agent Zero
echo "[3/3] Demarrage Agent Zero..."
source ~/.a0/.env.local
cd /chemin/vers/agent-zero
python main.py --config ~/.a0/config.yaml &

echo "✅ Infrastructure prete"
echo "   Hermes: http://localhost:8080"
echo "   Agent Zero: running"
echo "   Ollama API: http://localhost:8000"

EOF

chmod +x ~/.a0/unified_llm_launcher.sh
```

---

## 1️⃣1️⃣ Manque de Monitoring

### Diagnostic Détaillé
```
Type           : Visibilité nulle
Criticité      : STRATÉGIQUE (DevOps)
Impact         : Difficile diagnostiquer problèmes temps réel
Manquant       : Logs Agent Zero, métriques Ollama, alertes
Solution       : Stack monitoring (logs + metrics)
```

### Solution Complète

#### Étape 11.1 : Configurer Logging Agent Zero
```bash
# Déjà couverts dans config.yaml (problème #1)
# Vérifier logs disponibles:

# Affichage logs temps réel
tail -f ~/.a0/logs/agent_zero.log

# Monitoring avec filtres
tail -f ~/.a0/logs/agent_zero.log | grep -E "ERROR|WARNING|memorize_solutions"

# Chercher erreurs 401
grep "401\|AuthenticationError\|OpenRouter" ~/.a0/logs/agent_zero.log
```

#### Étape 11.2 : Monitorer Ollama
```bash
# Ressources Ollama
docker stats ollama --format "table {{.MemUsage}}\t{{.CPUPerc}}\t{{.MemPerc}}"

# Logs Ollama
docker logs -f ollama | grep -E "ERROR|request\|model"

# Modèles chargés
docker exec ollama ollama list

# Santé container
docker inspect ollama --format='{{json .State}}' | jq .
```

#### Étape 11.3 : Dashboard Monitoring (Optionnel)
```bash
# Créer script monitoring temps réel
cat > ~/.a0/monitor.sh << 'EOF'
#!/bin/bash

while true; do
    clear
    echo "=============== AGENT ZERO MONITORING ==============="
    echo "Timestamp: $(date)"
    echo ""
    
    echo "📊 OLLAMA:"
    docker stats ollama --no-stream --format "table {{.MemUsage}}\t{{.CPUPerc}}"
    echo ""
    
    echo "🤖 MODELES:"
    docker exec ollama ollama list | tail -5
    echo ""
    
    echo "⚠️ ERREURS RECENTES (Agent Zero):"
    tail -5 ~/.a0/logs/agent_zero.log | grep -i "error\|fail" || echo "Aucune"
    echo ""
    
    echo "🔌 API STATUS:"
    if curl -s http://localhost:8000/api/tags > /dev/null; then
        echo "✅ Ollama API: OK"
    else
        echo "❌ Ollama API: KO"
    fi
    
    echo ""
    echo "================= (F5 to refresh) ================="
    sleep 5
done

EOF

chmod +x ~/.a0/monitor.sh

# Lancer monitoring
~/.a0/monitor.sh
```

---

## 1️⃣2️⃣ Pas de Fallback Automatique

### Diagnostic Détaillé
```
Type           : Résilience faible
Criticité      : STRATÉGIQUE (disponibilité)
Impact         : Si OpenRouter échoue, pas de bascule → crash
Idéal          : Multi-provider avec priorité automatique
Config         : OpenRouter (PRIMARY) → Ollama (FALLBACK)
État actuel    : Provider unique sans fallback
```

### Solution Complète

#### Étape 12.1 : Configuration Multi-Provider
```bash
# Créer config avec fallback chain
cat > ~/.a0/config_with_fallback.yaml << 'EOF'
# Configuration Agent Zero - Multi-Provider avec Fallback
# Essaie providers dans ordre, bascule automatiquement en cas d'erreur

providers:
  # PRIMARY: Ollama local (recommandé)
  - provider: "ollama"
    enabled: true
    priority: 1
    config:
      base_url: "http://localhost:8000"
      model: "llama3.2:3b"
      timeout: 60
      fallback_on_error: true
  
  # SECONDARY: OpenRouter (désactivé de base)
  - provider: "openrouter"
    enabled: false
    priority: 2
    config:
      api_key: "${OPENROUTER_API_KEY}"
      model: "openrouter/llama2"
      timeout: 30
  
  # TERTIARY: OpenAI (désactivé de base)
  - provider: "openai"
    enabled: false
    priority: 3
    config:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-3.5-turbo"
      timeout: 30

# Extensions avec fallback
extensions:
  memorize_solutions:
    enabled: true
    fallback_to_local: true  # ← Crucial
    providers:
      - "ollama"
      - "openrouter"  # Si ollama échoue
      - "openai"       # Si openrouter échoue

# Monitoring et alertes
monitoring:
  enabled: true
  log_level: "DEBUG"
  alert_on_fallback: true
  alert_on_failure: true

EOF
```

#### Étape 12.2 : Implémenter Fallback Logic
```python
# Créer agent_zero_fallback.py
cat > ~/.a0/agent_zero_fallback.py << 'EOF'
#!/usr/bin/env python3
"""
Agent Zero Fallback System
Gère multi-provider avec fallback automatique
"""

import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)

class MultiProviderLLM:
    """LLM avec fallback automatique entre providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = config.get('providers', [])
        self.current_provider = None
        
    def chat(self, messages: list, model: str = None) -> Optional[str]:
        """
        Appelle LLM avec fallback automatique
        
        Logic:
        1. Essaie provider primaire (Ollama)
        2. Si erreur, essaie provider secondaire (OpenRouter)
        3. Si erreur, essaie provider tertiaire (OpenAI)
        4. Si tout échoue, log erreur critique
        """
        
        for provider_config in self.providers:
            if not provider_config.get('enabled'):
                continue
                
            provider_name = provider_config.get('provider')
            try:
                logger.info(f"Tentative avec {provider_name}...")
                
                if provider_name == 'ollama':
                    response = self._call_ollama(messages, model)
                elif provider_name == 'openrouter':
                    response = self._call_openrouter(messages, model)
                elif provider_name == 'openai':
                    response = self._call_openai(messages, model)
                else:
                    continue
                
                logger.info(f"✅ Succès avec {provider_name}")
                self.current_provider = provider_name
                return response
                
            except Exception as e:
                logger.warning(f"❌ {provider_name} échoué: {e}")
                continue
        
        logger.critical("❌ Tous les providers ont échoué!")
        return None
    
    def _call_ollama(self, messages: list, model: str) -> str:
        """Appel Ollama local"""
        config = self._get_provider_config('ollama')
        base_url = config['base_url']
        model = model or config['model']
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            },
            timeout=config.get('timeout', 60)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_openrouter(self, messages: list, model: str) -> str:
        """Appel OpenRouter (avec API key)"""
        config = self._get_provider_config('openrouter')
        api_key = config.get('api_key')
        
        if not api_key:
            raise Exception("OpenRouter API key manquante")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model or config['model'],
                "messages": messages
            },
            timeout=config.get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _call_openai(self, messages: list, model: str) -> str:
        """Appel OpenAI (avec API key)"""
        config = self._get_provider_config('openai')
        api_key = config.get('api_key')
        
        if not api_key:
            raise Exception("OpenAI API key manquante")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model or config['model'],
                "messages": messages
            },
            timeout=config.get('timeout', 30)
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _get_provider_config(self, provider: str) -> Dict:
        """Récupère config provider"""
        for p in self.providers:
            if p.get('provider') == provider:
                return p.get('config', {})
        raise Exception(f"Provider {provider} non configuré")

if __name__ == '__main__':
    import yaml
    
    # Charger config
    with open('config_with_fallback.yaml') as f:
        config = yaml.safe_load(f)
    
    # Créer LLM multi-provider
    llm = MultiProviderLLM(config)
    
    # Test
    response = llm.chat([
        {"role": "user", "content": "Bonjour!"}
    ])
    
    print(f"Réponse: {response}")
    print(f"Provider utilisé: {llm.current_provider}")

EOF

chmod +x ~/.a0/agent_zero_fallback.py
```

#### Étape 12.3 : Intégrer Fallback à Agent Zero
```bash
# Modifier main.py pour utiliser MultiProviderLLM

cat >> main.py.integration << 'EOF'
# Au démarrage d'Agent Zero, remplacer LLM simple par MultiProviderLLM:

from agent_zero_fallback import MultiProviderLLM
import yaml

# Charger config
with open(os.path.expanduser('~/.a0/config_with_fallback.yaml')) as f:
    config = yaml.safe_load(f)

# Créer LLM avec fallback
llm = MultiProviderLLM(config)

# Utiliser llm.chat() au lieu d'appels directs
EOF
```

#### Étape 12.4 : Monitoring Fallback
```bash
# Logs fallback
grep "MultiProviderLLM\|fallback\|provider.*échoué" ~/.a0/logs/agent_zero.log

# Statistiques fallbacks
cat > ~/.a0/stats_fallback.py << 'EOF'
#!/usr/bin/env python3
import re
from collections import defaultdict

# Lire logs
with open(os.path.expanduser('~/.a0/logs/agent_zero.log')) as f:
    logs = f.read()

# Compter fallbacks par provider
fallbacks = defaultdict(int)
for match in re.finditer(r'❌ (\w+) échoué', logs):
    fallbacks[match.group(1)] += 1

# Afficher stats
print("📊 Statistiques Fallbacks:")
for provider, count in sorted(fallbacks.items(), key=lambda x: -x[1]):
    print(f"  {provider}: {count} erreurs")

EOF

python3 ~/.a0/stats_fallback.py
```

---

# 📋 SYNTHÈSE ACTION - TOUS LES PROBLÈMES

| # | Problème | Type | Délai | Effort | État |
|---|----------|------|-------|--------|------|
| 1 | Auth 401 OpenRouter | 🚨 Critique | ⏰ Immédiat | 🟡 Moyen | ⏳ Étapes 1.1-1.5 |
| 2 | Config Agent Zero | 🚨 Critique | ⏰ Immédiat | 🟡 Moyen | ⏳ Voir prob. #1 |
| 3 | Ollama Non Démarré | 🚨 Critique | ⏰ Immédiat | 🟢 Facile | ⏳ Étapes 3.1-3.8 |
| 4 | Env Vars Non Héritées | ⚠️ Mineur | ⏰ 24h | 🟢 Facile | ⏳ Étapes 4.1-4.5 |
| 5 | Conflit PARAPLUIE | ⚠️ Mineur | ⏰ 24h | 🟡 Moyen | ⏳ Étapes 5.1-5.3 |
| 6 | Erreurs PowerShell | ⚠️ Mineur | ⏰ 24h | 🟢 Facile | ⏳ Étapes 6.1-6.4 |
| 7 | GPU Non Vérifié | 🔍 Latent | ⏰ 1 sem | 🟡 Moyen | ⏳ Étapes 7.1-7.5 |
| 8 | Modèles Non Téléchargés | 🔍 Latent | ⏰ 1 sem | 🟢 Facile | ⏳ Étapes 8.1-8.3 |
| 9 | Ports Occupés | 🔍 Latent | ⏰ 1 sem | 🟡 Moyen | ⏳ Étapes 9.1-9.3 |
| 10 | Double Config LLM | 🏗️ Architecte | 📅 Planifié | 🔴 Complexe | ⏳ Étapes 10.1-10.3 |
| 11 | Manque Monitoring | 🏗️ Architecte | 📅 Planifié | 🟡 Moyen | ⏳ Étapes 11.1-11.3 |
| 12 | Pas Fallback Auto | 🏗️ Architecte | 📅 Planifié | 🔴 Complexe | ⏳ Étapes 12.1-12.4 |

---

# 🎯 PLAN D'EXÉCUTION RECOMMANDÉ

## Phase 1 : URGENT (Aujourd'hui - 2h)
**Objectif :** Résoudre les 3 problèmes critiques
- [ ] **Problème #3** : Démarrer Ollama (Étapes 3.1-3.5)
- [ ] **Problème #1** : Configurer Agent Zero (Étapes 1.2-1.5)
- [ ] **Problème #2** : Créer config.yaml (Couvert par prob. #1)

**Validation :**
```bash
docker ps | grep ollama  # Ollama actif
curl http://localhost:8000/api/tags  # API répond
python ~/.a0/verify_config.py  # Config valide
```

## Phase 2 : IMPORTANT (Aujourd'hui à demain - 2h)
**Objectif :** Résoudre les problèmes mineurs
- [ ] **Problème #4** : Configurer vars d'env (Étapes 4.1-4.5)
- [ ] **Problème #5** : Nettoyer PARAPLUIE (Étapes 5.1-5.3)
- [ ] **Problème #6** : Fixer scripts PowerShell (Étapes 6.1-6.4)

**Validation :**
```bash
bash ~/.a0/run_agent_zero.sh  # Script lance correctement
tail -f ~/.a0/logs/agent_zero.log  # Logs sans erreur 401
```

## Phase 3 : MAINTENANCE (Cette semaine - 2h)
**Objectif :** Prévenir problèmes latents
- [ ] **Problème #7** : Vérifier GPU (Étapes 7.1-7.4)
- [ ] **Problème #8** : Télécharger modèles (Étapes 8.1-8.3)
- [ ] **Problème #9** : Vérifier ports (Étapes 9.1-9.3)

**Validation :**
```bash
nvidia-smi  # GPU détecté (optionnel)
docker exec ollama ollama list  # Modèles OK
netstat -tuln | grep -E "11434|8000"  # Ports OK
```

## Phase 4 : ARCHITECTURE (Planifié - 4h)
**Objectif :** Améliorer résilience long-terme
- [ ] **Problème #10** : Unifier LLM vers Ollama
- [ ] **Problème #11** : Mise en place monitoring
- [ ] **Problème #12** : Configurer fallback multi-provider

**Résultat final :**
```
✅ Agent Zero stable et autonome
✅ Infrastructure résiliente avec fallback
✅ Monitoring temps réel
✅ Documentation complète
```

---

**Document généré :** 2025-01  
**Version :** 1.0 Complète  
**Statut :** Prêt à exécuter par phases
