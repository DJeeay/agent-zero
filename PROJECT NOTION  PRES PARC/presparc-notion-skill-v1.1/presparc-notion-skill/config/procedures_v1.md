# Procédures Validées v1.0 — presparc-notion
## Présence-Parcours : séquences techniques de référence

**Version** : 1.0 — **Date** : 2026-03-01 — **Statut** : VALIDÉ PAR ENSEIGNANT  
Ces procédures sont immuables sans revalidation explicite. Référence pour `memory_save`.

---

## PROC-01 : Audit d'intégrité du workspace

**Déclencheur** : Chaque lundi 07h00 (cron `0 7 * * 1`) ou à la demande  
**Script** : `check_portal_integrity.py`  
**Durée estimée** : 15–30 secondes

### Séquence complète

```bash
# 1. Charger l'environnement
export $(cat /a0/usr/notion-agent/.env | xargs)

# 2. Lancer audit JSON
cd /a0/usr/skills/presparc-notion
python scripts/check_portal_integrity.py --json-only \
  2>> /a0/usr/notion-agent/logs/errors.log \
  | tee /tmp/audit_$(date +%Y%m%d).json

# 3. Analyser le résultat
python -c "
import json, sys
data = json.load(open('/tmp/audit_$(date +%Y%m%d).json'))
errors = sum(len(v) for db in data.get('databases', {}).values() for k,v in db.items() if isinstance(v,list))
print(f'AUDIT: {errors} anomalies détectées')
sys.exit(1 if errors > 0 else 0)
"

# 4. Logger résultat
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [INFO] [audit] Audit terminé" \
  >> /a0/usr/notion-agent/logs/execution.log
```

### Résultat attendu
- `errors == 0` → log "Audit OK" et continuer
- `errors > 0` → notifier enseignant avec contenu JSON, **ne pas auto-corriger**

### Codes de retour
- `0` = workspace sain
- `1` = anomalies détectées (notifier)
- `2` = erreur API (token/réseau — notifier immédiatement)

---

## PROC-02 : Génération automatique des comptes-rendus mensuels

**Déclencheur** : 1er de chaque mois à 08h00 (cron `0 8 1 * *`)  
**Script** : `generate_monthly_report.py`  
**Idempotence** : OUI — vérifie existence du CR avant création

### Séquence complète

```bash
# 1. Calculer mois précédent
YEAR=$(date -d "$(date +%Y-%m-01) -1 day" +%Y)
MONTH=$(date -d "$(date +%Y-%m-01) -1 day" +%m)
PERIOD="${YEAR}-${MONTH}"

# 2. Dry-run pour vérification
python scripts/generate_monthly_report.py \
  --month="${PERIOD}" \
  --dry-run \
  2>> /a0/usr/notion-agent/logs/errors.log

# 3. Génération réelle (en mode planifié, automatique)
python scripts/generate_monthly_report.py \
  --month="${PERIOD}" \
  2>> /a0/usr/notion-agent/logs/errors.log

# 4. Logger résultat
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [INFO] [generate_monthly_report] Période ${PERIOD} traitée" \
  >> /a0/usr/notion-agent/logs/execution.log
```

### Logique interne du script
1. Récupère tous les élèves actifs de BASE ELEVES
2. Pour chaque élève : requête BASE SEANCES filtrée par mois
3. Calcule statistiques : nb_seances, taux_devoirs, matieres_vues, duree_totale
4. Vérifie si CR existe déjà pour ce mois+élève (idempotence)
5. Si absent : crée page dans BASE COMPTES_RENDUS avec stats calculées
6. Met à jour le lien CR dans la fiche élève

### Propriétés créées automatiquement
- `Titre` : `CR {NOM} – {MOIS ANNÉE}`
- `Élève` : relation vers page élève
- `Période` : `YYYY-MM`
- `Nb séances ce mois` : entier
- `Taux présence (%)` : float calculé
- `Envoyé aux parents` : false (renseigné manuellement)
- `Points forts`, `Points à améliorer` : vides (renseignés manuellement par enseignant)

---

## PROC-03 : Normalisation du schéma (bootstrap)

**Déclencheur** : Manuel uniquement — jamais automatique  
**Script** : `bootstrap_schema.py`  
**⚠️ IRRÉVERSIBLE sans backup**

### Séquence obligatoire (ne jamais sauter une étape)

```
ÉTAPE 0 : Demander à l'enseignant : "Avez-vous exporté un backup Notion ?"
           → Attendre confirmation explicite ("oui" / "backup fait")

ÉTAPE 1 : dry-run
python scripts/bootstrap_schema.py --dry-run
→ Afficher toutes les actions prévues à l'enseignant

ÉTAPE 2 : Attendre validation
→ "Voici le plan. Confirmez avec 'OK' pour appliquer."

ÉTAPE 3 : apply
python scripts/bootstrap_schema.py --apply

ÉTAPE 4 : vérification post
python scripts/check_portal_integrity.py --json-only

ÉTAPE 5 : logger
echo "[$(date -u)] [INFO] [bootstrap_schema] Schéma normalisé v1.0" \
  >> /a0/usr/notion-agent/logs/execution.log
```

---

## PROC-04 : Création d'un portail famille

**Déclencheur** : Manuel — nouvel élève  
**Script** : `create_portail_famille.py`

### Prérequis
- Élève existant dans BASE ELEVES avec page_id connu
- Nom, prénom, niveau, matières confirmés par enseignant

### Séquence

```bash
# 1. Vérifier existence élève
python -c "
from utils.notion_api import get_page
page = get_page('ELEVE_PAGE_ID')
print(page['properties']['Nom complet'])
"

# 2. Dry-run
python scripts/create_portail_famille.py \
  --student-id="ELEVE_PAGE_ID" \
  --dry-run

# 3. Afficher structure prévue → attendre "OK" enseignant

# 4. Créer portail
python scripts/create_portail_famille.py \
  --student-id="ELEVE_PAGE_ID" \
  --apply

# 5. Récupérer URL portail et mettre à jour fiche élève
# 6. Logger et notifier
```

---

## PROC-05 : Enrichissement des bases OBJECTIFS et COMPTES_RENDUS

**Déclencheur** : Manuel — une seule fois à l'initialisation  
**Script** : `enrich_objectifs_comptes_rendus.py`

```bash
# Dry-run
python scripts/enrich_objectifs_comptes_rendus.py --dry-run

# Après confirmation enseignant
python scripts/enrich_objectifs_comptes_rendus.py --apply

# Vérification
python scripts/check_portal_integrity.py --json-only
```

---

## PROC-06 : Gestion et mémorisation d'une erreur API

**Déclencheur** : Automatique à chaque erreur API non gérée

### Format d'enregistrement mémoire

```json
{
  "text": "ERREUR API [CODE] [ENDPOINT] : [DESCRIPTION TECHNIQUE]\nCAUSE : [cause identifiée]\nFIX : [séquence de correction]\nVERIFICATION : [comment confirmer la résolution]",
  "metadata": {
    "area": "presparc_errors",
    "type": "error_fix",
    "error_code": "HTTP_CODE",
    "script": "script_concerné.py",
    "date": "YYYY-MM-DD",
    "validated": false,
    "version": "auto"
  }
}
```

### Règle d'apprentissage
- L'enregistrement est créé avec `"validated": false`
- L'enseignant valide le fix en répondant "validé" → metadata mise à jour
- Seuls les fixes `"validated": true` sont réutilisés automatiquement

---

## PROC-07 : Mise à jour d'une propriété élève (ad hoc)

**Déclencheur** : Manuel — à la demande de l'enseignant

```python
from utils.notion_api import update_page

# Exemple : mise à jour statut
update_page(
    page_id="ELEVE_PAGE_ID",
    properties={
        "Statut": {
            "select": {"name": "En pause"}
        }
    }
)
# Logger l'opération immédiatement
```

---

## INDEX DE MÉMORISATION (memory_save metadata)

| area | type | Contenu autorisé |
|---|---|---|
| `presparc_procedures` | `procedure` | Séquences API validées |
| `presparc_errors` | `error_fix` | Corrections d'erreurs techniques |
| `presparc_optimisations` | `optimisation` | Améliorations de performance |
| `presparc_schema` | `schema_note` | Notes sur les propriétés Notion |

**Contenu INTERDIT dans toute entrée mémoire :**  
Noms d'élèves, contenu pédagogique, données des parents, évaluations.
