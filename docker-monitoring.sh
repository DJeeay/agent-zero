#!/bin/bash
# docker-monitoring.sh
# Commandes de monitoring post-corrections

echo \"=== DOCKER SYSTEM STATUS ===\"
echo \"\"
echo \"Conteneurs:\"
docker ps -a --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\"
echo \"\"

echo \"=== RESSOURCES DISQUE ===\"
docker system df
echo \"\"

echo \"=== VÉRIFICATION MÉMOIRE ===\"
echo \"llama-server limits:\"
docker inspect llama-server --format '
Mémoire Hard Limit: {{.HostConfig.Memory | printf \"%.0f\" | unit_bytes}}
Mémoire Swap: {{.HostConfig.MemorySwap | printf \"%.0f\" | unit_bytes}}
CPU Limit: {{.HostConfig.CpuShares}}
CPU Nano: {{.HostConfig.NanoCpus}}
Restart Policy: {{.HostConfig.RestartPolicy.Name}}
'
echo \"\"

echo \"=== LOGS TEMPS RÉEL ===\"
echo \"llama-server (dernières 20 lignes):\"
docker logs llama-server --tail 20
echo \"\"
echo \"agent-zero (dernières 20 lignes):\"
docker logs agent-zero --tail 20
echo \"\"

echo \"=== MONITORING EN DIRECT ===\"
echo \"Appuyez sur Ctrl+C pour arrêter\"
docker stats llama-server agent-zero --no-stream
echo \"\"

# Statistiques détaillées
echo \"=== INSPECTION DÉTAILLÉE ===\"
echo \"llama-server:\"
docker inspect llama-server --format '
ID: {{.Id | trunc 12}}
Image: {{.Config.Image}}
Status: {{.State.Status}}
Health: {{.State.Health.Status}}
Uptime: {{.State.StartedAt}}
Memory Usage: {{.HostConfig.Memory}}
Network: {{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}
'

echo \"\"
echo \"agent-zero:\"
docker inspect agent-zero --format '
ID: {{.Id | trunc 12}}
Image: {{.Config.Image}}
Status: {{.State.Status}}
Uptime: {{.State.StartedAt}}
Volume: {{range .Mounts}}{{.Name}} {{end}}
Network: {{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}
'

echo \"\"
echo \"=== GPU UTILISATION ===\"
echo \"Note: Nécessite nvidia-docker\"
docker run --rm --gpus all nvidia/cuda:12.4.0-runtime-ubuntu22.04 nvidia-smi 2>/dev/null || echo \"GPU info non disponible (nvidia-docker requis)\"

