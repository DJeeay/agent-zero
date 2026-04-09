---
title: "Agent Zero + Hermes - Setup Local"
audience: ["Developer", "DevOps", "New User"]
level: "Beginner"
time_to_read: "15 min"
last_updated: "2025-04-05"
category: "DEPLOYMENT"
topic: "Local Setup"
related_docs:
  - "../01_INDEX.md"
  - "30_DEPLOYMENT_AGENT_ZERO_AUTH_ERROR.md"
  - "../OPERATIONS/20_OPERATIONS_COMMANDS.md"
  - "../TEMPLATES/50_TEMPLATES_DOCKER_COMPOSE.yml"
depends_on:
  - "Docker"
  - "Docker Compose"
  - "Hermes LLM"
---

# 🚀 Agent Zero + Hermes - Setup Local Présence-Parcours

## 📋 Vue d'ensemble

Configuration **personnalisée** d'Agent Zero avec :

- **Hermes LLM** local (llama.cpp)
- **RAG System** pour documentation Notion
- **Scheduler intelligent** 7 tâches automatiques
- **Skills spécialisées** Présence-Parcours

---

## ⚡ Quick Start

### Démarrage rapide

```bash
# Démarrer tout l'écosystème
docker-compose up -d

# Accéder aux services
Agent Zero UI : http://localhost:50080
Hermes API    : http://localhost:8081/v1
```

### Vérification

```bash
# Vérifier les conteneurs
docker ps --format "table {{.Names}}\t{{.Status}}"

# Monitoring Agent Zero
docker exec agent-zero python3 /a0/skills/monitor_agent.py
```

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Agent Zero    │───▶│   Hermes LLM     │───▶│  RAG System     │
│   Port: 50080   │    │   Port: 8081     │    │  - 49 docs      │
│   + 5 Skills    │    │   + Memory       │    │  - Notion Tech  │
│   + Scheduler   │    │   + Reasoning    │    │  - Fast Search  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 🤖 Skills Configurées

### 1. **RAG Integration** (`rag-integration.md`)

- Base FAISS avec 49 documents techniques Notion
- Recherche sémantique dans toute la technicité
- Intégration Hermes pour contexte enrichi

### 2. **Notion Technical Docs** (`notion-technical-docs.md`)

- Documentation complète API Notion
- Scripts, configuration, debugging
- 5 catégories auto-classifiées

### 3. **Notion Search** (`notion-search-skill.md`)

- Recherche rapide dans l'index technique
- Résultats avec métadonnées et sources
- Intégration naturelle Agent Zero

### 4. **Agent Memory & Tasks** (`agent-memory-tasks.md`)

- Gestion mémoire persistante
- 7 tâches automatiques programmées
- Intégration Hermes pour apprentissage

### 5. **Pres-Parc Notion** (`presparc-notion/SKILL.md`)

- Skill spécialisée Présence-Parcours
- Automatisation pédagogique
- Gestion élèves et séances

---

## ⏰ Tâches Automatiques

### Quotidiennes

- **6h** - Maintenance système + backup
- **8h** - Synchronisation Notion Présence-Parcours
- **22h** - Consolidation mémoire Hermes

### Hebdomadaires

- **Dimanche 2h** - Backup complet système
- **Samedi 18h** - Analyse performance

### Mensuelles

- **1er 3h** - Nettoyage profond mémoire
- **15 9h** - Mise à jour connaissances

---

## 📚 Base Connaissances RAG

### Documents Indexés : 49
- **notion_api** : 28 documents (API, endpoints)
- **debugging** : 10 documents (logs, erreurs)
- **scripting** : 6 documents (Python, automatisation)
- **configuration** : 4 documents (configs, settings)
- **deployment** : 1 document (déploiement)

### Recherche
```bash
# Dans Agent Zero UI
"Recherche les scripts Python d'automatisation Notion"
"Comment configurer l'API Notion pour Présence-Parcours ?"
"Trouve les procédures de debugging"
```

---

## 🔧 Configuration

### Ports Utilisés
- **50080** - Agent Zero Web UI
- **8081** - Hermes LLM API
- **8080** - (réservé, non utilisé)

### Fichiers Clés
- `docker-compose.yml` - Configuration conteneurs
- `settings.json` - Configuration Agent Zero
- `skills/` - Skills personnalisées
- `/a0/usr/scheduler/tasks.json` - Tâches planifiées
- `/a0/usr/projects/notion_technical_index.json` - Index RAG

---

## 🚀 Utilisation

### Commandes Agent Zero
> **"Indexe toute la technicité Notion"** ✅
> 
> **"Planifie une tâche urgente pour demain"** ✅
> 
> **"Montre-moi les tâches prévues aujourd'hui"** ✅
> 
> **"Recherche dans la documentation technique Notion"** ✅

### Monitoring
```bash
# Dashboard complet
docker exec agent-zero python3 /a0/skills/monitor_agent.py

# Lister tâches actives
docker exec agent-zero python3 /a0/skills/setup_agent_scheduler.py list

# Indexer Notion (si nécessaire)
docker exec agent-zero python3 /a0/skills/simple_notion_indexer.py
```

---

## 🎯 Présence-Parcours

### Integration Notion
- **Élèves** : Progression, séances, objectifs
- **Séances** : Planning, comptes-rendus automatiques
- **Objectifs** : Suivi pédagogique personnalisé
- **Portails Famille** : Pages automatiques pour parents

### Scripts Automatisés
- `check_portal_integrity.py` - Audit workspace
- `generate_monthly_report.py` - Comptes-rendus
- `enrich_objectifs_comptes_rendus.py` - Enrichissement données

---

## 🔍 Dépannage

### Problèmes Communs
| Symptôme | Solution |
|----------|----------|
| Agent Zero inaccessible | Vérifier `docker-compose up -d` |
| Hermes offline | `docker restart llamacpp` |
| RAG ne trouve rien | Relancer `simple_notion_indexer.py` |
| Tâches ne s'exécutent pas | Vérifier scheduler avec `setup_agent_scheduler.py list` |

### Logs
```bash
# Logs Agent Zero
docker logs agent-zero

# Logs Hermes
docker logs llamacpp

# Monitoring temps réel
docker exec agent-zero python3 /a0/skills/monitor_agent.py
```

---

## 📈 Performance

### État Actuel : 75% Opérationnel
- ✅ Scheduler : 7 tâches actives
- ✅ RAG System : 49 documents indexés
- ✅ Skills : 5 compétences spécialisées
- ⚠️ Hermes : Redémarrage parfois nécessaire
- ⚠️ Memory : Initialisation au démarrage

### Optimisations
- **Recherche RAG** : <100ms
- **Memory FAISS** : 86KB optimisé
- **Tâches auto** : Exécution parallèle
- **Hermes response** : ~500ms

---

## 🏆 Succès

Cette configuration **dépasse** le setup standard Agent Zero :
- 🧠 **Intelligence** : Hermes LLM + mémoire vectorielle
- 📋 **Organisation** : Scheduler intelligent automatisé
- 🔍 **Connaissance** : Base technique Notion complète
- 🎯 **Spécialisation** : Adapté Présence-Parcours
- 🤖 **Autonomie** : Maintenance et apprentissage

---

**Agent Zero est maintenant un véritable assistant IA autonome, spécialisé dans tes projets Présence-Parcours !** 🚀
