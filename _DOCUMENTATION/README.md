# 📚 _DOCUMENTATION - Bibliothèque Documentaire Docker

**Documentation centralisée pour l'infrastructure Docker Cont 1 AZ.**

Structure créée selon les recommandations Gordon - Architecture documentaire en 5 niveaux.

---

## 🗂️ Structure des Dossiers

```
_DOCUMENTATION/
│
├─ 00_START.md              ← Point d'entrée unique
├─ 01_INDEX.md              ← Hub de navigation
├─ 02_REGISTRY.yaml         ← Source de vérité (conteneurs, réseaux, volumes)
│
├─ 📂 REFERENCE/            ← Niveau 1: WHAT (Catalogues)
│  ├─ 10_REFERENCE_CONTAINERS_ANALYSIS.md
│  └─ 11_REFERENCE_RESUME_VISUAL.md
│
├─ 📂 OPERATIONS/           ← Niveau 2: HOW (Daily ops)
│  ├─ 20_OPERATIONS_COMMANDS.md
│  ├─ 21_OPERATIONS_FIXES.md
│  └─ 22_OPERATIONS_VERIFICATION.md
│
├─ 📂 DEPLOYMENT/           ← Niveau 3: HOW (Setup)
│  ├─ 30_DEPLOYMENT_AGENT_ZERO_AUTH_ERROR.md
│  └─ 31_DEPLOYMENT_LOCAL_SETUP.md
│
├─ 📂 ANALYSIS/             ← Niveau 4: DEEP DIVE
│  └─ 40_ANALYSIS_PROBLEMS_SOLUTIONS.md
│
└─ 📂 TEMPLATES/            ← Niveau 5: REUSABLE
   └─ 50_TEMPLATES_DOCKER_COMPOSE.yml
```

---

## 🎯 Convention de Nommage

**Pattern:** `[PRIORITY][CATEGORY]_[TOPIC].md`

| Code | Priorité | Catégorie |
|------|----------|-----------|
| 00-01 | Critique | Entry points |
| 10-19 | High | REFERENCE |
| 20-29 | High | OPERATIONS |
| 30-39 | Medium | DEPLOYMENT |
| 40-49 | Medium | ANALYSIS |
| 50-59 | Low | TEMPLATES |

**Avantages:**
- ✅ Tri naturel dans l'explorateur de fichiers
- ✅ Audience identifiable rapidement
- ✅ Recherche facile (`dir | findstr OPERATIONS`)

---

## 👤 Taxonomie par Audience

| Audience | Documents Prioritaires |
|----------|------------------------|
| **Manager/Décideur** | `00_START.md` → `11_REFERENCE_RESUME_VISUAL.md` |
| **DevOps/SRE** | `00_START.md` → `20_OPERATIONS_COMMANDS.md` |
| **Developer** | `30_DEPLOYMENT_*` → `50_TEMPLATES_*` |
| **Engineer** | `40_ANALYSIS_*` → `10_REFERENCE_*` |

---

## 📊 Métadonnées Documentaires

Chaque document contient un front-matter YAML:

```yaml
---
title: "Titre du Document"
audience: ["Developer", "DevOps"]
level: "Intermediate"
time_to_read: "15 min"
last_updated: "2025-04-05"
related_docs:
  - "REFERENCE/ARCHITECTURE.md"
  - "OPERATIONS/TROUBLESHOOTING.md"
---
```

---

## 🔗 Liens Bidirectionnels

Les documents sont interconnectés:
- `00_START.md` → tous les niveaux
- `01_INDEX.md` → hub de navigation
- Chaque doc → docs connexes dans son front-matter

---

## 🔄 Maintenance

**Responsabilités:**
- **Daily:** Operator vérifie logs (5 min)
- **Weekly:** Mise à jour `02_REGISTRY.yaml` (15 min)
- **Monthly:** Audit documentation architecture (1h)
- **Quarterly:** Révision complète (2h)

**Versioning:**
- Git tracking sur tous les changements
- `last_updated` dans chaque front-matter
- Commits avec message: `docs: description`

---

## 🚀 Démarrage Rapide

**Nouvel utilisateur?**
1. Lire `00_START.md` (3 min)
2. Consulter `01_INDEX.md` pour navigation (2 min)
3. Suivre le cheminement selon votre profil

**Besoin rapide?**
- Commandes: `20_OPERATIONS_COMMANDS.md`
- Troubleshooting: `22_OPERATIONS_VERIFICATION.md`
- Template: `50_TEMPLATES_DOCKER_COMPOSE.yml`

---

## 📈 Statistiques

| Métrique | Valeur |
|----------|--------|
| Documents | 11 |
| Niveaux | 5 |
| Templates | 1 |
| Conteneurs documentés | 8 (3 actifs + 5 arrêtés) |
| Réseaux | 9 |
| Volumes | 30 |

---

**Créé par:** Gordon (Documentation Manager)  
**Date:** 2025-04-05  
**Version:** 1.0
