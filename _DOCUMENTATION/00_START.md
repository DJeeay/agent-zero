---
title: "Docker Infrastructure Documentation - Start Here"
audience: ["All"]
level: "Beginner"
time_to_read: "3 min"
last_updated: "2025-04-05"
related_docs:
  - "01_INDEX.md"
  - "REFERENCE/ARCHITECTURE.md"
  - "OPERATIONS/QUICKSTART.md"
---

# 📚 Documentation Docker - Point d'Entrée

**Bienvenue dans la bibliothèque documentaire de Docker Cont 1 AZ.**

Ce dossier contient toute la documentation technique et opérationnelle de l'infrastructure Docker.

---

## 🎯 Je suis nouveau ici

**Commencez par :**
1. **[01_INDEX.md](./01_INDEX.md)** - Index de navigation central
2. **[REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md)** - Vue d'ensemble du système
3. **[OPERATIONS/QUICKSTART.md](./OPERATIONS/QUICKSTART.md)** - Démarrage rapide

---

## 📂 Structure de la Bibliothèque

```
_DOCUMENTATION/
│
├─ 00_START.md              ← Vous êtes ici
├─ 01_INDEX.md              ← Navigation centrale
│
├─ 📂 REFERENCE/            ← Niveau 1: WHAT (Catalogues)
│  ├─ ARCHITECTURE.md       ← Vue système complète
│  ├─ CONTAINERS.md         ← Catalogue conteneurs
│  └─ MODELS.md             ← Catalogue modèles LLM
│
├─ 📂 OPERATIONS/           ← Niveau 2: HOW (Daily ops)
│  ├─ QUICKSTART.md         ← 5 min setup
│  ├─ COMMANDS.md           ← Cheatsheet commandes
│  └─ TROUBLESHOOTING.md    ← Problèmes courants
│
├─ 📂 DEPLOYMENT/           ← Niveau 3: HOW (Setup)
│  ├─ DOCKER_SETUP.md     ← Configuration initiale
│  └─ AGENT_ZERO_SETUP.md   ← Setup spécifique A0
│
├─ 📂 ANALYSIS/             ← Niveau 4: DEEP DIVE
│  └─ TECHNICAL_ANALYSIS.md ← Analyses approfondies
│
└─ 📂 TEMPLATES/            ← Niveau 5: REUSABLE
   └─ docker-compose.template.yml
```

---

## 👤 Par profil utilisateur

### 🧑‍💼 Manager / Décideur
→ [REFERENCE/RESUME_VISUAL.md](./REFERENCE/RESUME_VISUAL.md) (5 min)  
→ [01_INDEX.md](./01_INDEX.md) section "Cheminement par Profil"

### 🔧 DevOps / SRE
→ [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) (10 min)  
→ [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) (15 min)

### 🏗️ Responsable Infrastructure
→ [ANALYSIS/TECHNICAL_ANALYSIS.md](./ANALYSIS/TECHNICAL_ANALYSIS.md) (20 min)  
→ [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md)

### 🆘 J'ai un problème maintenant
→ [OPERATIONS/TROUBLESHOOTING.md](./OPERATIONS/TROUBLESHOOTING.md)  
→ [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) section "FAQ"

---

## 🔍 Recherche rapide par problème

| Problème | Document |
|----------|----------|
| "Le système rame?" | → [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) |
| "Conteneur ne démarre pas?" | → [OPERATIONS/TROUBLESHOOTING.md](./OPERATIONS/TROUBLESHOOTING.md) |
| "Où est la config?" | → [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) |
| "Erreur d'authentification?" | → [DEPLOYMENT/AGENT_ZERO_SETUP.md](./DEPLOYMENT/AGENT_ZERO_SETUP.md) |
| "Comment monitorer?" | → [OPERATIONS/MONITORING.md](./OPERATIONS/MONITORING.md) |

---

## 🚨 État actuel du système

**Dernière mise à jour :** 2025-04-05

**Conteneurs actifs :**
- ✅ `llama-server` (port 8080) - Serveur LLM principal
- ✅ `llamacpp` (port 8081) - Serveur LLM backup
- ✅ `agent-zero` (port 50080) - Agent orchestrateur

**Documentation :**
- 📚 11 documents référencés
- 📁 5 niveaux de classification
- 🔗 Indexation centralisée

---

## 📝 Comment utiliser cette documentation

1. **Navigation** : Utilisez [01_INDEX.md](./01_INDEX.md) comme hub central
2. **Recherche** : Les documents sont préfixés par priorité (00, 01, 10, 20...)
3. **Métadonnées** : Chaque doc a un front-matter avec audience/niveau
4. **Liens** : Documents interconnectés avec liens bidirectionnels

---

## 🔄 Maintenance

Cette documentation est maintenue à jour via :
- **Git versionning** - Chaque changement = commit
- **Weekly refresh** - Vérification automatique hebdomadaire
- **Quarterly review** - Révision trimestrielle complète

---

**Besoin d'aide ?** Consultez [01_INDEX.md](./01_INDEX.md) ou cherchez par audience/niveau dans les métadonnées de chaque document.
