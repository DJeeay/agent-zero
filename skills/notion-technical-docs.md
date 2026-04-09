---
name: "notion-technical-docs"
description: "Documentation technique complète Notion pour Présence-Parcours. Scripts, API, configuration et dépannage avec recherche RAG intégrée."
version: "1.0.0"
author: "Agent Zero + Hermes RAG"
tags: ["notion", "technical", "documentation", "api", "scripts", "presparc"]
trigger_patterns:
  - "documentation notion"
  - "technique notion"
  - "scripts notion"
  - "api notion"
  - "configuration notion"
  - "dépanner notion"
  - "base de données notion"
---

# SKILL : Notion Technical Documentation

## Documentation Technique Complète Notion - Présence-Parcours

**Version** : 1.0.0  
**Dernière mise à jour** : 2026-04-02  
**Statut** : PRODUCTION - Indexé RAG  
**Domaine** : Technique Notion + Présence-Parcours  

---

## 0. IDENTITÉ ET PÉRIMÈTRE

Tu es **l'expert technique Notion** pour le projet Présence-Parcours, avec accès complet à toute la documentation technique via RAG.

**Ce que tu maîtrises :**
- API Notion complète et endpoints
- Scripts d'automatisation Python
- Configuration des bases de données
- Intégrations et workflows
- Dépannage et debugging
- Méthodes de sauvegarde et migration

**Ce que tu ne fais PAS :**
- Tu ne modifies JAMAIS les bases de production sans --dry-run
- Tu n'exposes JAMAIS les clés API dans les réponses
- Tu ne proposes JAMAIS de modifications sans validation
- Tu n'oublies JAMAIS de mentionner les sauvegardes

---

## 1. BASES DE DONNÉES NOTION PRÉSENCE-PARCOURS

### 1.1 Structure Principale
```
Présence-Parcours Workspace
├── ÉLÈVES (Base principale)
│   ├── Propriétés: Nom, Classe, Statut, Progression
│   ├── Relations: SEANCES, OBJECTIFS, ABSENCES
│   └── Automatisations: Calcul progression, Notifications
├── SÉANCES (Planning pédagogique)
│   ├── Propriétés: Date, Sujet, Compétences, Ressources
│   ├── Relations: ÉLÈVES, COMPTES_RENDUS
│   └── Vues: Calendrier, Par compétence, À venir
├── OBJECTIFS PÉDAGOGIQUES
│   ├── Propriétés: Compétence, Niveau, Critères, Validation
│   ├── Relations: ÉLÈVES, SEANCES
│   └── Suivi: Taux de réussite par compétence
└── ABSENCES ET RETARDS
    ├── Propriétés: Date, Motif, Justification, Rattrapage
    ├── Relations: ÉLÈVES
    └── Statistiques: Taux d'absentéisme, Trends
```

### 1.2 IDs des Bases (à utiliser avec précaution)
- **ÉLÈVES**: `[ID_BASE_ELEVES]`
- **SÉANCES**: `[ID_BASE_SEANCES]`
- **OBJECTIFS**: `[ID_BASE_OBJECTIFS]`
- **ABSENCES**: `[ID_BASE_ABSENCES]`

---

## 2. API NOTION - CONFIGURATION

### 2.1 Authentification
```python
# Configuration API sécurisée
NOTION_TOKEN = "secret_"  # Stocké dans .env uniquement
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}
```

### 2.2 Endpoints Principaux
```python
# Requêtes de base
BASE_URL = "https://api.notion.com/v1"

# Bases de données
GET_DATABASE = f"{BASE_URL}/databases/{{database_id}}"
QUERY_DATABASE = f"{BASE_URL}/databases/{{database_id}}/query"

# Pages
GET_PAGE = f"{BASE_URL}/pages/{{page_id}}"
CREATE_PAGE = f"{BASE_URL}/pages"
UPDATE_PAGE = f"{BASE_URL}/pages/{{page_id}}"

# Blocks
GET_BLOCK_CHILDREN = f"{BASE_URL}/blocks/{{block_id}}/children"
APPEND_BLOCK_CHILDREN = f"{BASE_URL}/blocks/{{block_id}}/children"
```

### 2.3 Rate Limiting
- **Limite**: 3 requêtes/secondes par intégration
- **Stratégie**: Backoff exponentiel
- **Monitoring**: Compteur de requêtes par minute

---

## 3. SCRIPTS D'AUTOMATISATION

### 3.1 Script Principal - Notion Agent
```python
# /a0/usr/notion-agent/main.py
class NotionAgent:
    def __init__(self):
        self.client = NotionClient()
        self.logger = setup_logging()
    
    def sync_all_bases(self):
        """Synchronisation complète des bases"""
        # 1. ÉLÈVES → Calcul progression
        # 2. SÉANCES → Mise à jour statuts
        # 3. OBJECTIFS → Validation automatique
        # 4. ABSENCES → Statistiques journalières
```

### 3.2 Scripts Spécialisés
- **`progression_calculator.py`** : Calcul automatique progression élèves
- **`attendance_tracker.py`** : Suivi des absences et retards
- **`report_generator.py`** : Génération comptes rendus automatiques
- **`backup_manager.py`** : Sauvegardes automatiques hebdomadaires

---

## 4. CONFIGURATION ET DÉPLOIEMENT

### 4.1 Variables Environnement
```bash
# .env configuration
NOTION_TOKEN=secret_*
NOTION_DATABASE_ELEVES=database_id_*
NOTION_DATABASE_SEANCES=database_id_*
NOTION_DATABASE_OBJECTIFS=database_id_*
NOTION_DATABASE_ABSENCES=database_id_*

LOG_LEVEL=INFO
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * 0"  # Dimanche 2h du matin
```

### 4.2 Docker Configuration
```yaml
# docker-compose.yml pour Notion Agent
notion-agent:
  image: python:3.11-slim
  volumes:
    - ./scripts:/app/scripts
    - ./logs:/app/logs
    - ./backups:/app/backups
  environment:
    - NOTION_TOKEN=${NOTION_TOKEN}
  restart: unless-stopped
```

---

## 5. DÉPANNAGE COMMUN

### 5.1 Erreurs API Fréquentes
```python
# Gestion des erreurs standards
try:
    response = notion_client.databases.query(database_id)
except HTTPResponseError as error:
    if error.code == "unauthorized":
        logger.error("Token Notion invalide ou expiré")
    elif error.code == "rate_limited":
        logger.warning("Rate limit atteint - attendre...")
        time.sleep(60)
    elif error.code == "object_not_found":
        logger.error("Base de données introuvable")
```

### 5.2 Solutions Problèmes Communs
- **Token expiré** : Régénérer dans les intégrations Notion
- **Base non trouvée** : Vérifier les partages et permissions
- **Rate limit** : Implémenter queue et retry avec backoff
- **Timeout** : Augmenter timeout et vérifier connexion

---

## 6. RECHERCHE RAG INTÉGRÉE

### 6.1 Utilisation avec Agent Zero
```
User: "Comment configurer l'API Notion pour Présence-Parcours ?"
Agent Zero: 
1. [RAG Search] → Documentation technique API
2. [Context] → Configuration sécurisée
3. [Response] → Guide étape par étape avec exemples
```

### 6.2 Types de Requêtes Supportées
- **Configuration**: "Comment configurer X"
- **Debugging**: "Erreur X dans Notion"
- **Scripts**: "Script pour faire X"
- **API**: "Endpoint pour X"
- **Best Practices**: "Meilleure pratique pour X"

---

## 7. WORKFLOWS AUTOMATISÉS

### 7.1 Workflow Quotidien
```python
# Exécution quotidienne automatique
def daily_workflow():
    # 1. Récupérer nouvelles séances du jour
    # 2. Mettre à jour statut élèves
    # 3. Calculer progression depuis dernière séance
    # 4. Envoyer notifications si nécessaire
    # 5. Logger toutes les opérations
```

### 7.2 Workflow Hebdomadaire
```python
def weekly_workflow():
    # 1. Générer rapport hebdomadaire
    # 2. Sauvegarder toutes les bases
    # 3. Nettoyer logs anciens
    # 4. Envoyer résumé à l'enseignant
```

---

## 8. SÉCURITÉ ET BONNES PRATIQUES

### 8.1 Sécurité API
- **Jamais** de token dans le code source
- **Toujours** utiliser variables d'environnement
- **Rotation** des tokens tous les 90 jours
- **Monitoring** des accès suspects

### 8.2 Bonnes Pratiques
- **Dry-run** avant modifications en masse
- **Backups** systématiques avant changements
- **Logging** détaillé de toutes les opérations
- **Validation** des données avant écriture

---

## 9. UTILISATION AGENT ZERO

### 9.1 Commandes Disponibles
```
# Recherche technique
"Trouve la documentation sur l'API Notion"
"Comment dépanner l'erreur rate_limited ?"
"Script pour synchroniser les élèves"

# Configuration  
"Montre-moi la configuration de base"
"Comment sécuriser les tokens Notion ?"
"Quelles sont les meilleures pratiques ?"

# Dépannage
"Pourquoi ma base ne se synchronise pas ?"
"Erreur 404 sur l'API Notion"
"Comment récupérer des données perdues ?"
```

### 9.2 Intégration Naturelle
Agent Zero utilisera automatiquement cette skill pour:
- Répondre aux questions techniques Notion
- Fournir des exemples de code
- Guider dans le dépannage
- Suggérer les meilleures pratiques

---

## 10. MAINTENANCE ET ÉVOLUTION

### 10.1 Maintenance Mensuelle
- **Vérifier** les logs d'erreurs
- **Mettre à jour** la documentation
- **Tester** les sauvegardes
- **Optimiser** les performances

### 10.2 Évolutions Prévues
- **v1.1** : Support multi-workspaces
- **v1.2** : Interface web de monitoring
- **v2.0** : IA prédictive pour progression
- **v2.1** : Intégration calendrier externe

---

**Cette skill transforme Agent Zero en expert technique Notion avec accès instantané à toute la documentation via RAG et mémoire Hermes.**
