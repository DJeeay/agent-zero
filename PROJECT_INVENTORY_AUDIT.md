# Audit des Projets Agent Zero - /a0/projects

## 📁 Structure globale

**Dossier analysé** : `/a0/projects`  
**Date d'audit** : 2025-04-06  
**Nombre de projets** : 5

---

## 📋 Inventaire des Projets

### 1. **kbd** (Keyboard Project)
| Attribut | Valeur |
|----------|--------|
| **Titre** | KBD |
| **Couleur** | #fb5607 (Orange) |
| **Memory** | own |
| **Fichiers clés** | `project.json`, `instructions/`, `knowledge/` |
| **Spécificités** | Structure minimaliste, pas de secrets/variables |
| **Agents** | Non configuré (pas de agents.json) |

### 2. **pres_parc_notion** (Projet Notion Principal) ⭐
| Attribut | Valeur |
|----------|--------|
| **Titre** | pres_parc_notion |
| **Couleur** | Non définie |
| **Memory** | Avec index FAISS |
| **Fichiers clés** | `project.json`, `agents.json`, `secrets.env`, `variables.env`, `run_sync.py`, `run_with_self_healing.py`, `setup_project.py`, `Skills/` |
| **Memory/Index** | ✅ **index.faiss** (27KB), **index.pkl** (50KB), embedding.json |
| **Instructions** | ✅ Présentes |
| **Knowledge** | ✅ Importé (knowledge_import.json) |
| **Agents** | {} (vide mais présent) |
| **Secrets** | 0 bytes (fichier vide) |
| **Variables** | 0 bytes (fichier vide) |
| **Scripts** | 4 scripts Python (sync, self-healing, test, setup) |

### 3. **project_ai_activity**
| Attribut | Valeur |
|----------|--------|
| **Titre** | Project_AI_Activity |
| **Couleur** | Non définie |
| **Memory** | own |
| **Fichiers clés** | `project.json`, `instructions/`, `knowledge/` |
| **Spécificités** | Structure minimaliste |
| **Agents** | Non configuré |

### 4. **project_win_restauration**
| Attribut | Valeur |
|----------|--------|
| **Titre** | Project_Win_Restauration |
| **Couleur** | #2563eb (Bleu) |
| **Memory** | own |
| **Fichiers clés** | `project.json`, `agents.json` (2 bytes = `{}`), `secrets.env` (0 bytes), `variables.env` (0 bytes), `instructions/`, `knowledge/` |
| **Agents** | {} (vide) |
| **Secrets/Variables** | Fichiers vides |

### 5. **projet_presence-parcours**
| Attribut | Valeur |
|----------|--------|
| **Titre** | Projet_Presence-Parcours |
| **Couleur** | #7b2cbf (Violet) |
| **Memory** | own |
| **Fichiers clés** | `project.json`, `agents.json` (2 bytes = `{}`), `secrets.env` (0 bytes), `variables.env` (0 bytes), `instructions/`, `knowledge/` |
| **Agents** | {} (vide) |
| **Secrets/Variables** | Fichiers vides |

---

## 🔍 Analyse comparative

### Configuration File Structure (Standard)
```
.a0proj/
├── project.json          ✅ Tous les projets (5/5)
├── agents.json           ⚠️ Seulement 3/5 (vide partout)
├── secrets.env          ⚠️ 3/5 présents mais vides
├── variables.env        ⚠️ 3/5 présents mais vides
├── instructions/         ✅ 5/5 (existence confirmée)
├── knowledge/            ✅ 5/5 (existence confirmée)
└── memory/               ⭐ 1/5 (seulement pres_parc_notion)
    ├── index.faiss       (FAISS vector index)
    ├── index.pkl         (Pickle index)
    ├── embedding.json    (Config embeddings)
    └── knowledge_import.json
```

### Différences clés par projet

| Projet | Agents | Secrets | Variables | Scripts Python | Index FAISS | Skills |
|--------|--------|---------|-----------|----------------|-------------|--------|
| kbd | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| pres_parc_notion | ✅ (vide) | ✅ (vide) | ✅ (vide) | ✅ (4) | ✅ | ✅ |
| project_ai_activity | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| project_win_restauration | ✅ (vide) | ✅ (vide) | ✅ (vide) | ❌ | ❌ | ❌ |
| projet_presence-parcours | ✅ (vide) | ✅ (vide) | ✅ (vide) | ❌ | ❌ | ❌ |

---

## 📊 Matrice de configuration

### Configuration project.json (Standard)
```json
{
  "title": "...",
  "description": "",
  "instructions": "",
  "color": "#hexcolor",
  "git_url": "",
  "memory": "own",
  "file_structure": {
    "enabled": true,
    "max_depth": 5,
    "max_files": 20,
    "max_folders": 20,
    "max_lines": 250,
    "gitignore": "# Python environments & cache\nvenv/**\n..."
  }
}
```

**Remarque** : Tous les projets utilisent la même configuration `file_structure` par défaut.

---

## 🎯 Points d'attention

### 🔴 Problèmes identifiés

1. **Agents non configurés** : Tous les `agents.json` sont vides `{}`
2. **Secrets non utilisés** : `secrets.env` et `variables.env` sont vides partout
3. **Fichiers inconsistants** : `pres_parc_notion/project.json.txt` (fichier en double avec extension .txt)
4. **Scripts orphelins** : `scriptstest_connections.py` (nom mal formaté)

### 🟢 Points positifs

1. **Index FAISS présent** : `pres_parc_notion` a un index de mémoire vectorielle fonctionnel
2. **Scripts utilitaires** : `pres_parc_notion` dispose de scripts avancés (sync, self-healing)
3. **Architecture propre** : Tous les projets suivent la structure .a0proj standard
4. **Configuration gitignore** : Exclusions appropriées (venv, node_modules, .git)

---

## 📍 Points d'entrée recommandés

### Pour navigation rapide :

| Besoin | Projet recommandé | Justification |
|--------|-------------------|---------------|
| **Développement Notion** | `pres_parc_notion` | Scripts complets, index FAISS, Skills |
| **Tests keyboard** | `kbd` | Projet simple, couleur orange distinctive |
| **IA/Activity tracking** | `project_ai_activity` | Nom explicite, structure propre |
| **Restauration Windows** | `project_win_restauration` | Thème spécifique, couleur bleue |
| **Présence/Parcours** | `projet_presence-parcours` | Couleur violette, thème formation |

### Fichiers critiques à vérifier :

1. **`/a0/projects/pres_parc_notion/.a0proj/project.json`** - Projet principal avec mémoire
2. **`/a0/projects/pres_parc_notion/.a0proj/memory/index.faiss`** - Index vectoriel FAISS
3. **`/a0/projects/pres_parc_notion/.a0proj/Skills/`** - Compétences personnalisées
4. **`/a0/projects/pres_parc_notion/.a0proj/run_sync.py`** - Script de synchronisation

---

## 📝 Résumé pour mémoire système

**ID Corpus** : d:/Hermes_AGENT  
**Entry Points** :
- `00_START.md` (général)
- `kbd/.a0proj/project.json` (KBD)
- `pres_parc_notion/.a0proj/project.json` (Notion principal)
- `project_ai_activity/.a0proj/project.json` (Activity)
- `project_win_restauration/.a0proj/project.json` (Windows)
- `projet_presence-parcours/.a0proj/project.json` (Parcours)

**Database IDs** : 
- FAISS index : `pres_parc_notion/.a0proj/memory/`

---

*Audit généré automatiquement - Agent Zero Project Inventory*
