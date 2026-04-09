# Guide de déploiement — presparc-notion sur Agent Zero
## Présence-Parcours v2.0 — 2026-03-01

## PRÉREQUIS
- [ ] Docker Desktop ou Docker CE installé (`docker --version` ≥ 24)
- [ ] Nouvelles clés API générées (Notion, Groq) — **révoquer les anciennes**
- [ ] VPN désactivé pour Groq (ou utiliser NVIDIA NIM)

## ÉTAPE 1 — Lancer Agent Zero avec volume persistant
```bash
mkdir -p ~/a0-data
docker run -d -p 50080:80 -v ~/a0-data:/a0/usr --name agent-zero agent0ai/agent-zero:latest
```
→ Accéder à http://localhost:50080

## ÉTAPE 2 — Configurer le LLM
**Groq (recommandé, sans VPN)** : provider=Groq, model=llama-3.3-70b-versatile
**Ollama (hors ligne)** : ollama pull llama3.2 && ollama pull nomic-embed-text
→ provider=Ollama, URL=http://host.docker.internal:11434
**NVIDIA NIM (si VPN)** : provider=OpenAI Compatible, URL=https://integrate.api.nvidia.com/v1

## ÉTAPE 3 — Déployer le skill
```bash
cp -r presparc-notion-skill ~/a0-data/skills/presparc-notion
mkdir -p ~/a0-data/notion-agent/logs
cp ~/a0-data/skills/presparc-notion/.env.example ~/a0-data/skills/presparc-notion/.env
# Éditer .env avec le nouveau NOTION_TOKEN
```

## ÉTAPE 4 — Installer les dépendances Python
```bash
docker exec -it agent-zero pip install -r /a0/usr/skills/presparc-notion/requirements.txt
```

## ÉTAPE 5 — Stocker les secrets dans Agent Zero
Envoyer dans Agent Zero :
```
Store: NOTION_TOKEN=[nouveau token], NOTION_VERSION=2022-06-28,
BASE_ELEVES_DB_ID=2e01652eed3f812db522f718ce5e8572,
BASE_SEANCES_DB_ID=2e01652eed3f812a9333e21d801ae37e,
BASE_OBJECTIFS_DB_ID=2e01652eed3f810ea862e5f232bfb0ce,
BASE_COMPTES_RENDUS_DB_ID=2e01652eed3f811f90ead738c9a4b7ac,
BASE_ABSENCES_DB_ID=fa3ffb04b9eb4a12bec367a0b119211f
```

## ÉTAPE 6 — Verrouiller le comportement
Envoyer le contenu de `.a0_docs/a0_behaviour_rules.json` dans Agent Zero.

## ÉTAPE 7 — Créer les tâches planifiées
Envoyer le contenu de `.a0_docs/scheduler_tasks.json` dans Agent Zero.

## ÉTAPE 8 — Initialiser la mémoire
Envoyer chaque entrée de `.a0_docs/memory_init.json` via memory_save.

## ÉTAPE 9 — Tests
```bash
docker exec -it agent-zero bash -c \
  "cd /a0/usr/skills/presparc-notion && python scripts/check_portal_integrity.py --json-only"
docker exec -it agent-zero bash -c \
  "cd /a0/usr/skills/presparc-notion && python scripts/generate_monthly_report.py --month=2026-02 --dry-run"
```

## COMMANDES QUOTIDIENNES
```bash
tail -f ~/a0-data/notion-agent/logs/execution.log   # logs temps réel
tail -f ~/a0-data/notion-agent/logs/errors.log      # erreurs
docker restart agent-zero                            # redémarrer sans perte
tar -czf backup_$(date +%Y%m%d).tar.gz ~/a0-data/  # backup complet
```

## RÉSOLUTION PROBLÈMES
| Erreur         | Cause                        | Solution                              |
|----------------|------------------------------|---------------------------------------|
| 401 Notion     | Token expiré                 | Renouveler sur notion.so/my-integrations |
| 403 Groq       | VPN actif                    | Désactiver VPN ou utiliser NVIDIA NIM |
| 404 Notion     | ID base incorrect            | Vérifier .env vs databases.json       |
| 429 Notion     | Rate limit (normal)          | Le script gère automatiquement        |
| ModuleNotFoundError | Dépendances manquantes  | pip install -r requirements.txt       |