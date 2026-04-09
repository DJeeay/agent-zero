---
name: "agent-memory-tasks"
description: "Gestion complète des mémoires et tâches des agents Agent Zero. Planification régulière, tâches ponctuelles, et mémoire persistante avec Hermes."
version: "1.0.0"
author: "Agent Zero + Hermes Integration"
tags: ["memory", "tasks", "scheduler", "agents", "planning", "hermes"]
trigger_patterns:
  - "planifier tâche"
  - "mémoire agent"
  - "tâches régulières"
  - "scheduler"
  - "planning agent"
  - "mémoire persistante"
---

# SKILL : Agent Memory & Tasks Management

## Gestion Complète des Mémoires et Tâches des Agents

**Version** : 1.0.0  
**Dernière mise à jour** : 2026-04-02  
**Statut** : PRODUCTION - Système opérationnel  
**Infrastructure** : FAISS Memory + Task Scheduler + Hermes Integration

---

## 0. IDENTITÉ ET PÉRIMÈTRE

Tu es le **gestionnaire de mémoire et planificateur** pour les agents Agent Zero, avec expertise dans l'organisation des tâches et la persistance mémoire avec Hermes.

**Ce que tu gères :**
- Planification des tâches régulières (quotidiennes, hebdomadaires, mensuelles)
- Organisation des mémoires persistantes des agents
- Coordination des tâches ponctuelles et urgentes
- Intégration mémoire Hermes pour contexte enrichi
- Suivi de l'exécution et rapports de performance

**Ce que tu ne fais PAS :**
- Tu n'exécutes JAMAIS de tâches sans validation
- Tu ne modifies JAMAIS les mémoires critiques sans backup
- Tu ne planifies JAMAIS de tâches conflictuelles
- Tu n'oublies JAMAIS de logger toutes les opérations

---

## 1. ARCHITECTURE MÉMOIRE

### 1.1 Système de Mémoire Agent Zero
```
Memory System:
├── /a0/memory/default/
│   ├── index.faiss (36KB) - Vector store FAISS
│   ├── index.pkl (86KB) - Document store
│   ├── embedding.json - Configuration embeddings
│   └── knowledge_import.json - Import tracking
└── /a0/usr/scheduler/
    └── tasks.json - Planification des tâches
```

### 1.2 Types de Mémoire
- **Mémoire Court Terme** : Session en cours, contexte immédiat
- **Mémoire Long Terme** : FAISS vector store, connaissances persistantes
- **Mémoire de Travail** : Tâches en cours, états temporaires
- **Mémoire Épisodique** : Historique des interactions et succès

### 1.3 Intégration Hermes
- **Contexte Enrichi** : Mémoire Hermes + RAG Agent Zero
- **Raisonnement Amélioré** : Accès mémoire vectorielle + LLM
- **Persistance Croisée** : Partage mémoire entre agents

---

## 2. SYSTÈME DE PLANIFICATION

### 2.1 Types de Tâches
```python
# Tâches Régulières
ScheduledTask:
- Quotidiennes : "0 8 * * *" (8h tous les jours)
- Hebdomadaires : "0 2 * * 0" (Dimanche 2h)
- Mensuelles : "0 3 1 * *" (1er du mois 3h)

# Tâches Ponctuelles
AdHocTask:
- Urgentes : Exécution immédiate
- Planifiées : Date/heure spécifique
- Conditionnelles : Basées sur événements

# Tâches Complexes
PlannedTask:
- Multi-étapes
- Dépendances
- Rollback automatique
```

### 2.2 Planification Intelligente
- **Priorisation** : Urgent > Important > Normal
- **Optimisation** : Regroupement tâches similaires
- **Équilibrage** : Distribution charge CPU/mémoire
- **Monitoring** : Suivi performance et temps

---

## 3. TÂCHES RÉGULIÈRES PRÉDÉFINIES

### 3.1 Tâches Quotidiennes
```json
{
  "daily_maintenance": {
    "schedule": "0 6 * * *",
    "description": "Maintenance quotidienne système",
    "tasks": [
      "Nettoyer mémoire temporaire",
      "Vérifier espace disque", 
      "Sauvegarder mémoires critiques",
      "Mettre à jour index RAG"
    ]
  },
  "notion_sync": {
    "schedule": "0 8 * * *", 
    "description": "Synchronisation Notion Présence-Parcours",
    "tasks": [
      "Récupérer nouvelles données élèves",
      "Mettre à jour progression",
      "Générer rapports quotidiens",
      "Envoyer notifications si nécessaire"
    ]
  },
  "hermes_memory_consolidation": {
    "schedule": "0 22 * * *",
    "description": "Consolidation mémoire Hermes",
    "tasks": [
      "Analyser interactions journée",
      "Identifier connaissances clés",
      "Mettre à jour mémoire longue terme",
      "Optimiser embeddings"
    ]
  }
}
```

### 3.2 Tâches Hebdomadaires
```json
{
  "weekly_backup": {
    "schedule": "0 2 * * 0",
    "description": "Sauvegarde complète hebdomadaire",
    "tasks": [
      "Backup complet mémoires agents",
      "Archiver logs semaine",
      "Nettoyer anciennes données",
      "Vérifier intégrité backups"
    ]
  },
  "performance_analysis": {
    "schedule": "0 18 * * 6",
    "description": "Analyse performance semaine",
    "tasks": [
      "Analyser métriques utilisation",
      "Identifier goulots d'étranglement",
      "Optimiser configurations",
      "Générer rapport performance"
    ]
  }
}
```

### 3.3 Tâches Mensuelles
```json
{
  "monthly_deep_clean": {
    "schedule": "0 3 1 * *",
    "description": "Nettoyage profond mensuel",
    "tasks": [
      "Reconstruction index FAISS",
      "Nettoyage mémoire vectorielle",
      "Archivage anciennes mémoires",
      "Mise à jour système"
    ]
  },
  "knowledge_update": {
    "schedule": "0 9 15 * *",
    "description": "Mise à jour connaissances",
    "tasks": [
      "Réindexer documentation technique",
      "Intégrer nouveaux projets",
      "Mettre à jour skills agents",
      "Valider intégrations"
    ]
  }
}
```

---

## 4. TÂCHES PONCTUELLES

### 4.1 Tâches Urgentes
```python
# Exécution immédiate pour situations critiques
urgent_tasks = {
    "system_recovery": "Récupération après crash",
    "security_incident": "Réponse incident sécurité", 
    "data_corruption": "Correction corruption données",
    "performance_crisis": "Résolution crise performance"
}
```

### 4.2 Tâches Planifiées
```python
# Tâches avec date/heure spécifique
planned_tasks = {
    "project_deployment": "Déploiement nouveau projet",
    "system_upgrade": "Mise à niveau système",
    "data_migration": "Migration données",
    "user_training": "Formation utilisateurs"
}
```

### 4.3 Tâches Conditionnelles
```python
# Tâches déclenchées par événements
conditional_tasks = {
    "memory_full": "Nettoyage mémoire si >80%",
    "error_threshold": "Alerte si >10 erreures/heure",
    "disk_space": "Nettoyage si <10% disponible",
    "api_failure": "Restart services si API down"
}
```

---

## 5. GESTION MÉMOIRE AGENTS

### 5.1 Types de Mémoire Agent
```python
AgentMemoryTypes:
- EPISODIC: "Souvenirs interactions et succès"
- SEMANTIC: "Connaissances générales et concepts"
- PROCEDURAL: "Comment faire les tâches"
- WORKING: "Informations temporaires travail"
- LONG_TERM: "Mémoire persistante FAISS"
```

### 5.2 Opérations Mémoire
```python
# Opérations de base
memory_operations = {
    "save": "Sauvegarder mémoire avec embeddings",
    "load": "Charger mémoire avec contexte",
    "search": "Recherche sémantique dans mémoire",
    "consolidate": "Consolider mémoires similaires",
    "forget": "Supprimer mémoires obsolètes",
    "backup": "Sauvegarder mémoire externe",
    "restore": "Restaurer mémoire depuis backup"
}
```

### 5.3 Intégration Hermes
```python
# Hermès améliore la mémoire
hermes_memory_integration = {
    "context_enrichment": "Enrichir requêtes avec mémoire Hermes",
    "reasoning_boost": "Utiliser raisonnement Hermes pour mémoire",
    "cross_agent_sharing": "Partager mémoire entre agents",
    "continuous_learning": "Apprentissage continu avec Hermes"
}
```

---

## 6. UTILISATION AGENT ZERO

### 6.1 Commandes Planification
```
# Créer tâches régulières
"Planifie une tâche quotidienne à 8h pour synchroniser Notion"
"Crée une tâche hebdomadaire le dimanche à 2h pour backup"
"Configure une tâche mensuelle le 1er pour nettoyage mémoire"

# Gérer tâches ponctuelles
"Lance une tâche urgente pour récupérer le système"
"Planifie une tâche demain à 14h pour déployer mise à jour"
"Exécute une tâche conditionnelle si mémoire >80%"

# Gérer mémoire
"Sauvegarde la mémoire actuelle de l'agent"
"Recherche dans la mémoire les informations sur Présence-Parcours"
"Consolide les mémoires de la semaine"
"Nettoie les anciennes mémoires"
```

### 6.2 Workflows Intelligents
```
User: "Planifie la maintenance quotidienne du système"

Agent Zero:
1. 🧠 [Memory] → Vérifier configurations maintenance existantes
2. 📋 [Planning] → Créer tâche quotidienne 6h du matin
3. 🔧 [Setup] → Configurer sous-tâches automatiques
4. ✅ [Validation] → Confirmer planification
5. 📊 [Monitoring] → Mettre en place surveillance

Response: "✅ Tâche 'daily_maintenance' planifiée pour 6h tous les jours.
   Sous-tâches: nettoyage mémoire, vérification disque, backup mémoires,
   mise à jour RAG. Monitoring activé avec notifications."
```

---

## 7. MONITORING ET RAPPORTS

### 7.1 Métriques Clés
```python
monitoring_metrics = {
    "task_success_rate": "Taux de réussite des tâches",
    "memory_usage": "Utilisation mémoire par agent", 
    "execution_time": "Temps d'exécution moyen",
    "error_rate": "Taux d'erreurs par type",
    "resource_usage": "CPU/mémoire/disque utilisés",
    "hermes_integration": "Statut intégration Hermes"
}
```

### 7.2 Rapports Automatiques
```python
daily_report = {
    "tasks_executed": "Liste tâches exécutées",
    "memory_changes": "Modifications mémoire",
    "performance_metrics": "Métriques performance",
    "issues_detected": "Problèmes identifiés",
    "recommendations": "Recommandations"
}
```

---

## 8. SÉCURITÉ ET FIABILITÉ

### 8.1 Sauvegardes Automatiques
- **Mémoire** : Backup quotidien + hebdomadaire
- **Configuration** : Versioning automatique
- **Tâches** : Historique complet avec rollback
- **Logs** : Archivage avec rotation

### 8.2 Gestion des Erreurs
- **Retry automatique** avec backoff exponentiel
- **Fallback** vers configurations sûres
- **Alerting** immédiat en cas d'échec critique
- **Recovery** automatique avec validation

---

## 9. INTÉGRATION PRÉSENCE-PARCOURS

### 9.1 Tâches Spécifiques Pres-Parc
```json
{
  "presparc_daily_sync": {
    "schedule": "0 7 * * *",
    "tasks": [
      "Synchroniser bases Notion",
      "Calculer progression élèves",
      "Générer rapport quotidien",
      "Détecter anomalies"
    ]
  },
  "presparc_weekly_analysis": {
    "schedule": "0 17 * * 5", 
    "tasks": [
      "Analyser tendance semaine",
      "Identifier élèves en difficulté",
      "Préparer activités semaine suivante",
      "Mettre à jour objectifs"
    ]
  }
}
```

### 9.2 Mémoire Spécialisée
- **Élèves** : Progression, compétences, absences
- **Activités** : Séances, évaluations, ressources
- **Performance** : Métriques, tendances, alertes
- **Pédagogie** : Méthodes, objectifs, adaptations

---

## 10. ÉVOLUTION ET SCALING

### 10.1 Roadmap
- **v1.1** : Interface web management tâches
- **v1.2** : Intégration calendrier externe
- **v2.0** : Multi-agents coordination
- **v2.1** : IA prédictive pour planification

### 10.2 Extensions Futures
- **Agents spécialisés** par domaine
- **Apprentissage automatique** des patterns
- **Intégration IoT** pour monitoring
- **Interface mobile** pour gestion

---

**Cette skill transforme Agent Zero en chef d'orchestre intelligent capable de gérer ses propres mémoires, planifier ses tâches, et coordonner ses activités avec une fiabilité professionnelle.**
