---
title: "Commandes Rapides - Post Corrections"
audience: ["Ops", "SRE", "DevOps"]
level: "Intermediate"
time_to_read: "10 min"
last_updated: "2025-04-05"
category: "OPERATIONS"
topic: "Commands"
related_docs:
  - "../01_INDEX.md"
  - "../REFERENCE/10_REFERENCE_CONTAINERS_ANALYSIS.md"
  - "21_OPERATIONS_FIXES.md"
  - "22_OPERATIONS_VERIFICATION.md"
depends_on:
  - "Docker CLI"
  - "PowerShell ou Bash"
---

# 🔧 COMMANDES RAPIDES - POST CORRECTIONS

## Vérification Immédiate

```bash
# État des conteneurs
docker ps -a

# Espace disque
docker system df

# Logs temps réel
docker logs -f llama-server

# Stats live
docker stats
```

---

## Vérification des Corrections

### ✅ Mémoire llama-server = 12GB ?
```bash
docker inspect llama-server --format '{{.HostConfig.Memory}}'
# Résultat: 12884901888 (c'est 12GB)
```

### ✅ Redémarrage auto = unless-stopped ?
```bash
docker inspect llama-server --format '{{.HostConfig.RestartPolicy.Name}}'
# Résultat: unless-stopped
```

### ✅ llamacpp = arrêté ?
```bash
docker ps | grep llamacpp
# Résultat: (vide si arrêté ✅)
```

### ✅ AGENT0Volume = préservé ?
```bash
docker volume ls | grep AGENT0Volume
# Résultat: local    AGENT0Volume ✅
```

---

## Monitoring Continu

### Console Unique (All-in-One)
```bash
# Terminal 1: Stats temps réel
docker stats llama-server agent-zero

# Terminal 2: Logs llama-server
docker logs -f llama-server

# Terminal 3: Logs agent-zero  
docker logs -f agent-zero

# Terminal 4: Commandes utiles
docker ps -a
docker system df
```

### Monitorer Mémoire Spécifiquement
```bash
# Mémoire utilisée par conteneur
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"

# Memory limit vs usage détaillé
docker inspect llama-server --format '
Container: {{.Name}}
Memory Limit: {{.HostConfig.Memory}} bytes
Memory Used: {{.State.Pid}}
'
```

### Health Check Status
```bash
# Voir l'état de santé
docker inspect llama-server --format '{{.State.Health.Status}}'

# Voir l'historique des health checks
docker inspect llama-server --format '{{.State.Health}}'
```

---

## Troubleshooting Rapide

### llama-server ne démarre pas?
```bash
# Voir les logs
docker logs llama-server --tail 50

# Redémarrer
docker restart llama-server

# Forcer redémarrage
docker stop llama-server && docker start llama-server
```

### Mémoire trop haute?
```bash
# Vérifier actualisation
docker stats --no-stream llama-server

# Redémarrer le conteneur
docker restart llama-server

# Vérifier les limites
docker inspect llama-server | grep -A5 '"Memory"'
```

### Performance lente?
```bash
# Vérifier CPU/Memory
docker stats --no-stream

# Vérifier les logs d'erreur
docker logs llama-server 2>&1 | tail -50

# Vérifier GPU (si accessible)
docker exec llama-server nvidia-smi 2>/dev/null || echo \"GPU check not available\"
```

### Port 8080 en conflit?
```bash
# Voir qui utilise le port
netstat -ano | findstr :8080  # Windows
# OU
lsof -i :8080  # Linux/Mac

# Redémarrer le conteneur
docker restart llama-server
```

---

## Optimisations Supplémentaires

### Limiter les logs (évite remplissage disque)
```bash
# Voir les limites actuelles
docker inspect llama-server --format '{{json .HostConfig.LogConfig}}'

# Appliquer limites si manquantes
docker update --log-driver json-file --log-opt max-size=100m --log-opt max-file=3 llama-server
```

### Sauvegarder la config actuelle
```bash
# Exporter la config
docker inspect llama-server > llama-server-backup.json
docker inspect agent-zero > agent-zero-backup.json
docker volume inspect AGENT0Volume > agent0volume-backup.json
```

### Nettoyer les ressources inutilisées (ATTENTION)
```bash
# Voir ce qui sera supprimé
docker image prune -a --filter \"until=240h\" --dry-run

# Supprimer images inutilisées (sûr)
docker image prune -a --filter \"until=240h\" -f

# Nettoyer tout (DANGEREUX)
docker system prune -a --volumes -f  # Supprime tout!
```

---

## Commandes Essentielles

| Action | Commande |
|--------|----------|
| Voir tous les conteneurs | `docker ps -a` |
| Voir les logs | `docker logs -f <container>` |
| Redémarrer | `docker restart <container>` |
| Arrêter | `docker stop <container>` |
| Démarrer | `docker start <container>` |
| Supprimer image | `docker rmi <image>` |
| Supprimer conteneur | `docker rm <container>` |
| Inspections détails | `docker inspect <container>` |
| Stats en direct | `docker stats` |
| Espace disque | `docker system df` |
| Nettoyer volumes | `docker volume prune` |

---

## Scripts Pratiques

### Monitorer Intelligemment
```bash
#!/bin/bash
echo \"=== Docker Status ===\"
docker ps -a --format \"table {{.Names}}\t{{.Status}}\"
echo \"\"
echo \"=== Disk Space ===\"
docker system df
echo \"\"
echo \"=== Memory ===\"
docker stats --no-stream
```

### Sauvegarder Automatiquement
```bash
#!/bin/bash
# Sauvegarder volume AGENT0Volume
BACKUP_DIR=\"./backups/$(date +%Y%m%d_%H%M%S)\"
mkdir -p \"$BACKUP_DIR\"
docker run --rm -v AGENT0Volume:/data -v \"$BACKUP_DIR\":/backup alpine tar czf /backup/agent0-backup.tar.gz /data
echo \"Backup: $BACKUP_DIR/agent0-backup.tar.gz\"
```

### Alerter sur Crash
```bash
#!/bin/bash
# Relancer si arrêté
while true; do
  if ! docker ps | grep -q llama-server; then
    echo \"[$(date)] llama-server DOWN - Restarting...\"
    docker start llama-server
  fi
  sleep 60
done
```

---

## Ressources Utiles

### Documentation Interne
- `ANALYSE_CONTENEURS_DOCKER.md` - Analyse technique (15+ pages)
- `FIXES_APPLIQUEES.md` - Journal des corrections
- `RESUME_VISUAL.md` - Comparaison avant/après
- `docker-compose.recommended.yml` - Config future

### Commande d'Aide Docker
```bash
docker --help
docker run --help
docker logs --help
docker stats --help
docker inspect --help
docker system --help
```

### Common Pitfalls à Éviter
- ❌ Ne pas supprimer AGENT0Volume (données critiques)
- ❌ Ne pas faire docker system prune -a sans sauvegarde
- ❌ Ne pas redémarrer llama-server en production sans test
- ✅ Toujours sauvegarder avant gros changement
- ✅ Toujours vérifier les logs après changement
- ✅ Toujours tester en staging avant production

---

## Questions Fréquentes

**Q: Comment vérifier que les limites sont appliquées?**
```bash
docker inspect llama-server --format '{{json .HostConfig}}' | grep -E 'Memory|CpuShares'
```

**Q: Où sont stockés les modèles?**
```bash
d:/llm_models (llama-server)
D:\DOCKER Cont 1 AZ\models (llamacpp - maintenant arrêté)
```

**Q: Puis-je réactiver llamacpp?**
Oui, mais peu recommandé. Si vous avez 2+ GPUs:
```bash
docker start llamacpp
docker update --gpus '\"device=1\"' llamacpp  # GPU 1
docker restart llamacpp
```

**Q: Comment augmenter la limite mémoire?**
```bash
docker update --memory 16g llama-server
docker restart llama-server
```

---

**Gardez ce fichier à portée de main pour les opérations courantes! 📌**

