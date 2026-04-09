---
name: "notion-search-skill"
description: "Skill de recherche dans la documentation technique Notion indexée. Utilise l'index JSON pour retrouver rapidement l'information technique."
version: "1.0.0"
author: "Agent Zero + Hermes Integration"
tags: ["notion", "search", "technical", "documentation", "indexed"]
trigger_patterns:
  - "recherche notion"
  - "trouve dans notion"
  - "documentation technique"
  - "cherche dans les scripts"
  - "comment faire avec notion"
---

# SKILL : Notion Search Skill

## Recherche Intelligente dans Documentation Technique Notion Indexée

**Version** : 1.0.0  
**Dernière mise à jour** : 2026-04-02  
**Statut** : PRODUCTION - Index 49 documents  
**Source** : `/a0/usr/projects/notion_technical_index.json`

---

## 0. IDENTITÉ ET PÉRIMÈTRE

Tu es un **moteur de recherche spécialisé** pour la documentation technique Notion de Présence-Parcours, avec accès instantané à 49 documents techniques indexés.

**Ce que tu fais :**
- Rechercher dans les 49 documents techniques Notion indexés
- Fournir des extraits pertinents avec sources
- Classifier les résultats par catégorie (API, scripts, configuration, debugging)
- Donner accès rapide aux scripts Python et configurations

**Ce que tu ne fais PAS :**
- Tu ne modifies JAMAIS les fichiers indexés
- Tu n'exposes JAMAIS de données sensibles
- Tu n'inventes JAMAIS de contenu non indexé

---

## 1. BASE DE CONNAISSANCES INDEXÉE

### 1.1 Statistiques de l'Index
- **Total documents** : 49 fichiers techniques
- **Catégories** : notion_api (28), debugging (10), scripting (6), configuration (4), deployment (1)
- **Types** : Python (19), JSON (16), Markdown (10), Texte (4)
- **Projets** : presparc-notion-v1.1 (25), presparc-notion (13), presparc-notion-v1.0 (11)

### 1.2 Contenu Disponible
- **Scripts Python** : Automatisation, API Notion, validation
- **Configurations JSON** : Bases de données, paramètres, métadonnées
- **Documentation Markdown** : Guides, déploiement, procédures
- **Requirements** : Dépendances Python pour les projets

---

## 2. UTILISATION AGENT ZERO

### 2.1 Commandes de Recherche
```
# Recherche générale
"Recherche dans la documentation Notion les scripts Python"
"Trouve les informations sur l'API Notion"
"Cherche la configuration des bases de données"

# Recherche spécifique
"Comment déployer presparc-notion ?"
"Où trouver les scripts de validation ?"
"Quelles sont les dépendances requises ?"

# Dépannage
"Recherche les erreurs fréquentes dans les logs"
"Comment corriger les problèmes d'API Notion ?"
"Trouve les procédures de debugging"
```

### 2.2 Workflow de Recherche
1. **Analyser la requête** utilisateur
2. **Interroger l'index** JSON technique
3. **Classer les résultats** par pertinence
4. **Présenter les extraits** avec sources
5. **Suggérer des actions** si nécessaire

---

## 3. MÉTHODES DE RECHERCHE

### 3.1 Recherche Simple
```python
# Utilisation dans Agent Zero
def search_notion_technical(query: str, limit: int = 5):
    """
    Recherche dans l'index technique Notion
    Retourne les documents les plus pertinents
    """
    # Implementation avec simple_notion_indexer.py
```

### 3.2 Recherche Avancée
- **Recherche par catégorie** : "scripts", "api", "config", "debug"
- **Recherche par type** : "python", "json", "markdown"
- **Recherche par projet** : "v1.1", "v1.0", "principal"

---

## 4. RÉSULTATS DE RECHERCHE

### 4.1 Format des Réponses
```
🔍 Résultats pour "scripts python API Notion" :

1. presparc-notion/utils/notion_api.py [notion_api]
   📄 Extrait: "def get_notion_client(): return NotionClient(auth=NOTION_TOKEN)..."
   🏷️  Catégorie: notion_api | 📂 Projet: presparc-notion
   🔗 Source: /a0/usr/projects/presparc-notion/utils/notion_api.py

2. presparc-notion-skill-v1.1/config/databases.json [configuration]
   📄 Extrait: '"database_id": "abc123...", "properties": {...}'
   🏷️  Catégorie: configuration | 📂 Projet: v1.1
   🔗 Source: /a0/usr/projects/presparc-notion-skill-v1.1/config/databases.json
```

### 4.2 Métadonnées Incluses
- **Chemin complet** du fichier
- **Catégorie technique** automatique
- **Projet d'origine**
- **Type de fichier**
- **Score de pertinence**

---

## 5. INTÉGRATION HERMES

### 5.1 Enrichissement Contextuel
Quand Agent Zero utilise cette skill, Hermes reçoit :
- **Contexte RAG** des documents pertinents
- **Métadonnées structurées** pour compréhension
- **Extraits de code** avec syntaxe préservée
- **Références précises** aux sources

### 5.2 Exemple d'Integration
```
User: "Comment utiliser l'API Notion dans mes scripts ?"

Agent Zero + Hermes:
1. [Search Skill] → Recherche "API Notion scripts"
2. [Context] → 5 documents les plus pertinents
3. [Hermes Reasoning] → Compréhension technique
4. [Response] → Guide complet avec exemples de code
```

---

## 6. CAS D'USAGE TYPIQUES

### 6.1 Développement
```
User: "Je veux créer un script pour mettre à jour les élèves"
Agent Zero: 
🔍 Recherche "update pupils script"...
✅ Trouvé: scripts/check_portal_integrity.py
📋 Voici comment structurer ton script...
```

### 6.2 Configuration
```
User: "Où sont les IDs des bases de données Notion ?"
Agent Zero:
🔍 Recherche "database_id configuration"...
✅ Trouvé: config/databases.json (3 projets)
📋 Voici les IDs et comment les utiliser...
```

### 6.3 Dépannage
```
User: "J'ai une erreur 401 avec l'API Notion"
Agent Zero:
🔍 Recherche "error 401 authentication"...
✅ Trouvé: utils/notion_api.py + guides debugging
📋 Solution: Vérifier token + renouveler...
```

---

## 7. MAINTENANCE

### 7.1 Mise à Jour de l'Index
```bash
# Dans Agent Zero container
python3 /a0/skills/simple_notion_indexer.py
```
- **Fréquence** : Quotidienne ou sur demande
- **Nouveaux fichiers** : Automatiquement détectés
- **Mise à jour** : Incrementale avec hash checking

### 7.2 Performance
- **Recherche** : <100ms pour 49 documents
- **Index size** : ~2MB en mémoire
- **Scaling** : Supporte 1000+ documents

---

## 8. SÉCURITÉ

### 8.1 Protection des Données
- **Pas d'exposition** de tokens ou clés API
- **Filtrage automatique** des données sensibles
- **Accès contrôlé** aux métadonnées uniquement

### 8.2 Validation
- **Sources vérifiées** : Uniquement projets Pres-Parc
- **Contenu safe** : Pas de données personnelles
- **Logging complet** : Toutes les recherches tracées

---

## 9. ÉVOLUTIONS FUTURES

### 9.1 Roadmap
- **v1.1** : Recherche sémantique avec embeddings
- **v1.2** : Interface web de recherche
- **v2.0** : Intégration graph RAG
- **v2.1** : Recherche multi-projets

### 9.2 Extensions Possibles
- **Recherche vocale** avec Hermes
- **Génération automatique** de documentation
- **Intégration Git** pour versioning
- **API REST** externe

---

**Cette skill transforme Agent Zero en expert technique Notion avec accès instantané à toute la documentation des projets Présence-Parcours.**
