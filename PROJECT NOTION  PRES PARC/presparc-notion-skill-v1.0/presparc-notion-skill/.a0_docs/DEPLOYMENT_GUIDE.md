# Guide de déploiement complet — presparc-notion sur Agent Zero
## Présence-Parcours v2.0 — 2026-03-01

---

## PRÉREQUIS

- [ ] Docker Desktop ou Docker CE installé et fonctionnel
- [ ] `docker --version` retourne une version ≥ 24
- [ ] Clés API **révoquées et renouvelées** (Notion, Groq, OpenRouter…)
  - Notion : https://www.notion.so/my-integrations
  - Groq : https://console.groq.com
- [ ] VPN désactivé pour la connexion à Groq (ou exception ajoutée)
- [ ] Dossier local créé pour le volume persistant (ex: `~/a0-data`)

---

## ÉTAPE 1 — Lancer Agent Zero avec volume persistant
D:\DOCKER Cont 1 AZ\presparc-notion-skill-v1.0\presparc-notion-skill\.a0_docs
```bash
# Créer le dossier de données persistantes
mkdir -p ~/a0-data

# Lancer le conteneur
docker run -d \ 
  -p 50080:80 \
  -v ~/a0-data:/a0/usr \
  --name agent-zero \
  agent0ai/agent-zero:latest

# Vérifier que le conteneur tourne
docker ps | grep agent-zero

# Accéder à l'interface web
# → http://localhost:50080
```

---

## ÉTAPE 2 — Configurer le modèle LLM

### Option A — Groq (recommandé, sans VPN)
Dans Agent Zero → Settings → External Services :
- **Chat model provider** : Groq
- **Chat model** : `llama-3.3-70b-versatile`
- **API Key** : votre nouvelle clé Groq (recrée sur console.groq.com)
- **Utility model** : `llama-3.1-8b-instant`

### Option B — Ollama local (100% hors ligne)
```bash
# Sur la machine hôte
ollama pull llama3.2
ollama pull nomic-embed-text
```
Dans Agent Zero → Settings :
- **Provider** : Ollama
- **Base URL** : `http://host.docker.internal:11434`
- **Chat model** : `llama3.2`
- **Embedding model** : `nomic-embed-text`

### Option C — NVIDIA NIM (si VPN incontournable)
- **Provider** : OpenAI Compatible
- **Base URL** : `https://integrate.api.nvidia.com/v1`
- **API Key** : votre clé NVIDIA (renouvelée)
- **Chat model** : `meta/llama-3.1-70b-instruct`

---

## ÉTAPE 3 — Déployer le skill presparc-notion

```bash
# Copier les fichiers du skill dans le volume monté
cp -r ./presparc-notion-skill ~/a0-data/skills/presparc-notion

# Vérifier la structure
ls ~/a0-data/skills/presparc-notion/
# Doit afficher : SKILL.md  config/  scripts/  utils/  output/  requirements.txt

# Créer les dossiers de logs
mkdir -p ~/a0-data/notion-agent/logs
mkdir -p ~/a0-data/notion-agent/backups
```

---

## ÉTAPE 4 — Configurer le fichier .env

```bash
cd ~/a0-data/skills/presparc-notion

# Copier le template
cp .env.example .env

# Éditer avec vos vraies valeurs
nano .env
```

Valeurs à renseigner dans `.env` :
```
NOTION_TOKEN=ntn_NOUVEAU_TOKEN_NOTION
NOTION_VERSION=2022-06-28
BASE_ELEVES_DB_ID=2e01652eed3f812db522f718ce5e8572
BASE_SEANCES_DB_ID=2e01652eed3f812a9333e21d801ae37e
BASE_OBJECTIFS_DB_ID=2e01652eed3f810ea862e5f232bfb0ce
BASE_COMPTES_RENDUS_DB_ID=2e01652eed3f811f90ead738c9a4b7ac
BASE_ABSENCES_DB_ID=fa3ffb04b9eb4a12bec367a0b119211f
```

---

## ÉTAPE 5 — Installer les dépendances Python dans le conteneur

```bash
# Entrer dans le conteneur
docker exec -it agent-zero bash

# Installer les dépendances
pip install -r /a0/usr/skills/presparc-notion/requirements.txt

# Tester l'import
python -c "import requests; from dotenv import load_dotenv; print('OK')"
```

---

## ÉTAPE 6 — Stocker les secrets dans Agent Zero

Dans l'interface Agent Zero, envoyer ce message :

```
Store the following secrets (use §§secret() format for all future references):
- NOTION_TOKEN = [votre nouveau token]
- NOTION_VERSION = 2022-06-28
- BASE_ELEVES_DB_ID = 2e01652eed3f812db522f718ce5e8572
- BASE_SEANCES_DB_ID = 2e01652eed3f812a9333e21d801ae37e
- BASE_OBJECTIFS_DB_ID = 2e01652eed3f810ea862e5f232bfb0ce
- BASE_COMPTES_RENDUS_DB_ID = 2e01652eed3f811f90ead738c9a4b7ac
- BASE_ABSENCES_DB_ID = fa3ffb04b9eb4a12bec367a0b119211f
```

---

## ÉTAPE 7 — Verrouiller le comportement de l'agent

Dans l'interface Agent Zero, envoyer le contenu de `.a0_docs/a0_behaviour_rules.json`  
(copier-coller la valeur du champ `"tool_args"` directement dans le chat).

Ou envoyer ce message :
```
Apply permanent behaviour rules from file /a0/usr/skills/presparc-notion/.a0_docs/a0_behaviour_rules.json
```

---

## ÉTAPE 8 — Créer les tâches planifiées

Dans l'interface Agent Zero, envoyer :

**Tâche 1 — Audit hebdomadaire (chaque lundi 07h00) :**
```
Create a scheduled task named "presparc_audit_hebdomadaire" with cron "0 7 * * 1" that runs:
cd /a0/usr/skills/presparc-notion && python scripts/check_portal_integrity.py --json-only
Log result to /a0/usr/notion-agent/logs/execution.log. Notify me on error.
```

**Tâche 2 — Rapport mensuel (1er du mois, 08h00) :**
```
Create a scheduled task named "presparc_rapport_mensuel" with cron "0 8 1 * *" that:
1. Calculates the previous month (YYYY-MM format)
2. Runs: cd /a0/usr/skills/presparc-notion && python scripts/generate_monthly_report.py --month=PREV_MONTH
3. Logs result to /a0/usr/notion-agent/logs/execution.log
4. Notifies me with: "Comptes-rendus mensuels générés. Complétez Points forts / Points à améliorer dans Notion."
```

---

## ÉTAPE 9 — Test de validation

```bash
# Test audit complet (doit retourner 0 erreurs si schéma OK)
docker exec -it agent-zero bash -c \
  "cd /a0/usr/skills/presparc-notion && \
   python scripts/check_portal_integrity.py --json-only"

# Test dry-run rapport mensuel
docker exec -it agent-zero bash -c \
  "cd /a0/usr/skills/presparc-notion && \
   python scripts/generate_monthly_report.py --month=2026-02 --dry-run"
```

---

## CHECKLIST FINALE

- [ ] Agent Zero accessible sur http://localhost:50080
- [ ] LLM configuré et fonctionnel (test : "Bonjour" → réponse obtenue)
- [ ] Volume `/a0/usr` persistant (vérifier après restart du conteneur)
- [ ] Skill `presparc-notion` dans `/a0/usr/skills/`
- [ ] `.env` renseigné avec le nouveau token Notion
- [ ] Dépendances Python installées dans le conteneur
- [ ] Secrets stockés dans Agent Zero
- [ ] Règles de comportement appliquées
- [ ] Tâches planifiées créées (audit + rapport)
- [ ] Test d'audit retourne 0 erreurs
- [ ] Test dry-run rapport mensuel fonctionne
- [ ] **Clés de l'ancien chat RÉVOQUÉES et régénérées**

---

## Commandes utiles au quotidien

```bash
# Voir les logs en temps réel
tail -f ~/a0-data/notion-agent/logs/execution.log

# Voir les erreurs
tail -f ~/a0-data/notion-agent/logs/errors.log

# Lancer un audit manuellement
docker exec -it agent-zero bash -c \
  "cd /a0/usr/skills/presparc-notion && python scripts/check_portal_integrity.py"

# Backup du volume complet
tar -czf backup_a0_$(date +%Y%m%d).tar.gz ~/a0-data/

# Redémarrer Agent Zero sans perte de données
docker restart agent-zero
```

---

## Résolution des problèmes fréquents

| Problème | Cause probable | Solution |
|---|---|---|
| `401 Unauthorized` | Token Notion expiré ou révoqué | Renouveler le token sur notion.so/my-integrations |
| `403 Forbidden` (Groq) | VPN actif | Désactiver VPN ou utiliser option B/C |
| `404 Not Found` | ID de base incorrect | Vérifier `.env` avec les IDs de `databases.json` |
| `429 Too Many Requests` | Rate limit Notion | Normal, le script attend automatiquement (0.35s) |
| `ModuleNotFoundError` | Dépendances non installées | `pip install -r requirements.txt` dans le conteneur |
| Logs vides | Dossier `/a0/usr/notion-agent/logs` inexistant | `mkdir -p ~/a0-data/notion-agent/logs` |
