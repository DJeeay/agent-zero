---
title: "Documentation Index - Navigation Hub"
audience: ["All"]
level: "All Levels"
time_to_read: "5 min"
last_updated: "2025-04-05"
related_docs:
  - "00_START.md"
  - "REFERENCE/ARCHITECTURE.md"
  - "OPERATIONS/QUICKSTART.md"
---

# 📋 INDEX DE NAVIGATION - Docker Infrastructure

**Hub central de la documentation Docker Cont 1 AZ.**

Ce document vous guide vers la bonne documentation selon votre besoin.

---

## 📚 Les 5 Niveaux Documentaires

### Niveau 1: REFERENCE (WHAT)
Documentation descriptive - "Qu'est-ce que c'est ?"

| Document | Description | Audience |
|----------|-------------|----------|
| [ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) | Vue système complète | Architectes, SRE |
| [CONTAINERS.md](./REFERENCE/CONTAINERS.md) | Catalogue des conteneurs | DevOps, Ops |
| [MODELS.md](./REFERENCE/MODELS.md) | Catalogue modèles LLM | Data Engineers |

### Niveau 2: OPERATIONS (HOW - Daily)
Documentation procédurale quotidienne

| Document | Description | Audience |
|----------|-------------|----------|
| [QUICKSTART.md](./OPERATIONS/QUICKSTART.md) | Démarrage rapide 5 min | Nouveaux ops |
| [COMMANDS.md](./OPERATIONS/COMMANDS.md) | Cheatsheet commandes | Ops quotidien |
| [TROUBLESHOOTING.md](./OPERATIONS/TROUBLESHOOTING.md) | Problèmes & solutions | SRE |
| [MONITORING.md](./OPERATIONS/MONITORING.md) | Health checks & métriques | SRE |

### Niveau 3: DEPLOYMENT (HOW - Setup)
Documentation de configuration et déploiement

| Document | Description | Audience |
|----------|-------------|----------|
| [DOCKER_SETUP.md](./DEPLOYMENT/DOCKER_SETUP.md) | Setup Docker initial | DevOps |
| [AGENT_ZERO_SETUP.md](./DEPLOYMENT/AGENT_ZERO_SETUP.md) | Config Agent Zero | Developers |

### Niveau 4: ANALYSIS (DEEP DIVE)
Analyses techniques approfondies

| Document | Description | Audience |
|----------|-------------|----------|
| [TECHNICAL_ANALYSIS.md](./ANALYSIS/TECHNICAL_ANALYSIS.md) | Analyse conteneurs (15+ pages) | Architects |
| [PROBLEMS_SOLUTIONS.md](./ANALYSIS/PROBLEMS_SOLUTIONS.md) | Problèmes techniques détaillés | Engineers |

### Niveau 5: TEMPLATES (REUSABLE)
Templates et configurations réutilisables

| Document | Description | Audience |
|----------|-------------|----------|
| [docker-compose.template.yml](./TEMPLATES/docker-compose.template.yml) | Template Docker Compose | DevOps |
| [.env.template](./TEMPLATES/.env.template) | Template variables env | DevOps |

---

## 🎯 Cheminement par Profil

### 👤 Manager / Décideur (7 minutes)
1. Lire: [RESUME_VISUAL.md](./REFERENCE/RESUME_VISUAL.md) (5 min)
2. Parcourir: Section "État actuel" ci-dessous (2 min)

### 👤 DevOps / SRE (22 minutes)
1. Lire: [00_START.md](./00_START.md) (2 min)
2. Consulter: [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) (5 min)
3. Vérifier: [OPERATIONS/MONITORING.md](./OPERATIONS/MONITORING.md) (10 min)
4. Adapter: Templates si besoin (5 min)

### 👤 Responsable Infrastructure (50 minutes)
1. Lire: [ANALYSIS/TECHNICAL_ANALYSIS.md](./ANALYSIS/TECHNICAL_ANALYSIS.md) (20 min)
2. Valider: [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) (15 min)
3. Vérifier: [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) (10 min)
4. Planifier: Prochaines étapes (5 min)

### 👤 Nouvel Opérateur (25 minutes)
1. Lire: [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) - Vue d'ensemble (10 min)
2. Mémoriser: [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) (10 min)
3. Pratiquer: Exécuter les commandes (5 min)

---

## 🔍 Recherche Rapide par Problème

### "Le système rame?"
→ [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) section "Performance"

### "Où est mon volume Agent-Zero?"
→ [OPERATIONS/TROUBLESHOOTING.md](./OPERATIONS/TROUBLESHOOTING.md) FAQ

### "Quel était le problème?"
→ [REFERENCE/RESUME_VISUAL.md](./REFERENCE/RESUME_VISUAL.md) section "Avant/Après"

### "Je dois réactiver llamacpp"
→ [OPERATIONS/TROUBLESHOOTING.md](./OPERATIONS/TROUBLESHOOTING.md)

### "Comment monitorer?"
→ [OPERATIONS/MONITORING.md](./OPERATIONS/MONITORING.md)

### "Données sûres?"
→ [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) section "Stockage"

### "Prochaines étapes?"
→ [OPERATIONS/MAINTENANCE.md](./OPERATIONS/MAINTENANCE.md)

### "Configuration future?"
→ [TEMPLATES/docker-compose.template.yml](./TEMPLATES/docker-compose.template.yml)

---

## 📊 État Actuel du Système

**Dernière mise à jour:** 2025-04-05

### Conteneurs Actifs

| Conteneur | Port | Statut | Description |
|-----------|------|--------|-------------|
| llama-server | 8080 | ✅ Running | Serveur LLM principal (Hermes 3.1 8B) |
| llamacpp | 8081 | ✅ Running | Serveur LLM backup |
| agent-zero | 50080 | ✅ Running | Agent orchestrateur |

### Métriques Clés

| Métrique | Valeur | Impact |
|----------|--------|--------|
| Conteneurs actifs | 3 | Stable |
| Volumes persistants | 30 | Optimisation nécessaire |
| Réseaux | 9 | Standard |
| Espace disque | +5.82 GB récupéré | ✅ Optimisé |

### Documentation

| Type | Nombre | Statut |
|------|--------|--------|
| Documents référencés | 11 | ✅ Indexés |
| Niveaux de classification | 5 | ✅ Actifs |
| Templates disponibles | 2 | ✅ Prêts |

---

## ✅ Checklist de Vérification

### Système
- [x] Tous les conteneurs critiques actifs ✅
- [x] Mémoire llama-server limitée ✅
- [x] GPU alloué correctement ✅
- [x] Redémarrage auto activé ✅
- [x] Volumes critiques préservés ✅

### Documentation
- [x] Structure _DOCUMENTATION créée ✅
- [x] 00_START.md entry point ✅
- [x] 01_INDEX.md navigation hub ✅
- [x] Documents classifiés par niveau ✅
- [x] Liens bidirectionnels ✅

---

## 🚀 Prochaines Actions Recommandées

### Aujourd'hui
```bash
# Vérifier l'état des conteneurs
docker stats llama-server agent-zero

# Vérifier les logs
docker logs -f llama-server
```

### Cette Semaine
- Consulter [OPERATIONS/MAINTENANCE.md](./OPERATIONS/MAINTENANCE.md)
- Vérifier les métriques de performance
- Mettre à jour les configs si nécessaire

### Prochaines Semaines
- Prometheus + Grafana (monitoring avancé)
- Alertes automatisées
- Backups automatiques

---

## 📞 Support & Questions

### Documentation Manquante?
→ Consulter [ANALYSIS/TECHNICAL_ANALYSIS.md](./ANALYSIS/TECHNICAL_ANALYSIS.md) (le plus complet)

### Besoin d'une Commande?
→ Consulter [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md)

### Besoin de Contexte Technique?
→ Consulter [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md)

### Besoin de Configurer?
→ Consulter [DEPLOYMENT/DOCKER_SETUP.md](./DEPLOYMENT/DOCKER_SETUP.md)

### Besoin d'Auditer?
→ Consulter [ANALYSIS/TECHNICAL_ANALYSIS.md](./ANALYSIS/TECHNICAL_ANALYSIS.md)

---

## 🎓 Documents par Format

### Pages Longues (lecture profonde)
- [ANALYSIS/TECHNICAL_ANALYSIS.md](./ANALYSIS/TECHNICAL_ANALYSIS.md) (15+ pages)
- [REFERENCE/ARCHITECTURE.md](./REFERENCE/ARCHITECTURE.md) (10+ pages)

### Guides Opérationnels (exécution)
- [OPERATIONS/COMMANDS.md](./OPERATIONS/COMMANDS.md) (6 pages)
- [OPERATIONS/MONITORING.md](./OPERATIONS/MONITORING.md) (script)

### Résumés (overview)
- [00_START.md](./00_START.md) (3 pages)
- [REFERENCE/RESUME_VISUAL.md](./REFERENCE/RESUME_VISUAL.md) (5 pages)

### Configuration (IaC)
- [TEMPLATES/docker-compose.template.yml](./TEMPLATES/docker-compose.template.yml)

---

## 📝 Notes de Maintenance

**Processus de mise à jour:**
1. Chaque changement = commit Git
2. Weekly refresh automatique
3. Quarterly review manuelle

**Responsabilités:**
- Daily: Operator monitors logs
- Weekly: DevOps updates procedures
- Monthly: Update architecture docs
- Quarterly: Full review

---

**Tous les documents sont prêts à l'emploi. Sélectionnez celui qui correspond à votre besoin! 🎉**
