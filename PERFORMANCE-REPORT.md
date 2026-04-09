# OpenAgents Performance Report

## Executive Summary

Ce rapport analyse les performances des agents OpenAgents configurés avec différents modèles LLM locaux. Les tests ont été réalisés sur une machine avec GPU NVIDIA RTX 3060 (12GB VRAM).

## Test Configuration

### Hardware
- **GPU**: NVIDIA RTX 3060 (12GB VRAM)
- **RAM**: Non spécifiée
- **OS**: Windows

### Models Tested
1. **Hermes-3-Llama-3.1-8B.Q4_K_M** (8B params, 4-bit quantized)
2. **NVIDIA Nemotron-3-Nano-4B** (4B params)

### Test Prompts
1. "Hello" (Simple greeting)
2. "What is 2+2?" (Basic math)
3. "Explain photosynthesis in one sentence" (Science explanation)
4. "Write a Python function that adds two numbers" (Code generation)
5. "Summarize the history of artificial intelligence" (Complex topic)

## Performance Results

### Response Time Analysis

| Agent | Avg Response Time | Fastest | Slowest | Range |
|-------|------------------|---------|---------|-------|
| **Hermes-3** | 1,734 ms | 565 ms | 2,946 ms | 2,381 ms |
| **Nemotron-3-Nano** | 3,273 ms | 691 ms | 5,539 ms | 4,848 ms |

### Performance by Prompt Type

#### Simple Prompts ("Hello", "What is 2+2?")
- **Hermes-3**: 565-1,745 ms (excellent)
- **Nemotron-3-Nano**: 691-4,019 ms (good)

#### Medium Prompts ("Explain photosynthesis", "Write Python function")
- **Hermes-3**: 955-2,461 ms (good)
- **Nemotron-3-Nano**: 2,238-3,879 ms (acceptable)

#### Complex Prompts ("Summarize AI history")
- **Hermes-3**: 2,946 ms (acceptable)
- **Nemotron-3-Nano**: 5,539 ms (slow but detailed)

### Tokens/Second Analysis

| Agent | Tokens/sec | Avg Tokens/Response | Quality |
|-------|------------|---------------------|---------|
| **Hermes-3** | -0.83* | -1* | Fast but token counting broken |
| **Nemotron-3-Nano** | 39.88 | 143.2 | Detailed responses |

*Note: Hermes-3 token counting shows -1 due to adapter bug

## Bottlenecks Identified

### 1. Token Counting Bug (Critical)
**Issue**: L'adaptateur FastAPI de Hermes retourne `-1` pour tous les tokens
**Impact**: Impossible de mesurer correctement les tokens/seconde
**Status**: Corrigé dans `adapter-fixed.py` mais non déployé

### 2. Latence Variance
**Issue**: Temps de réponse très variables (565ms - 5,539ms)
**Causes**:
- Chargement initial du modèle
- Cache prompts non optimisé
- GPU memory management

### 3. Architecture Overhead
**Issue**: Nemotron 2x plus lent que Hermes
**Causes**:
- LM Studio vs Docker overhead
- Modèle 4B vs 8B (inverse de ce qu'on attendrait)
- Différences d'optimisation GPU

## Optimization Recommendations

### Immediate Actions (High Priority)

1. **Déployer l'adaptateur corrigé**
   ```bash
   docker cp adapter-fixed.py hermes:/app/adapter.py
   docker restart hermes
   ```

2. **Optimiser les paramètres GPU**
   - Augmenter `n_gpu_layers` pour Hermes-3
   - Optimiser `batch_size` pour Nemotron

3. **Activer le cache prompts**
   - Paramètre `cache_prompt: true` déjà activé
   - Vérifier l'efficacité du cache

### Medium Priority

1. **Configuration par cas d'usage**
   - **Questions simples**: Hermes-3 (plus rapide)
   - **Code/explications détaillées**: Nemotron-3-Nano

2. **Monitoring en continu**
   - Mettre en place des alertes de latence > 3s
   - Surveiller l'utilisation GPU/RAM

### Long Term

1. **Tester d'autres modèles**
   - Qwen3.5-0.8B (ultra-rapide)
   - Llama-3.1-8B-Instruct (alternative à Hermes)

2. **Optimisation Docker**
   - GPU memory pinning
   - Shared memory optimization

## Usage Recommendations

### Pour les Réponses Rapides
**Utiliser**: `hermes-local` ou `cagent-hermes`
- Temps moyen: 1.7s
- Idéal pour: Chat simple, questions directes

### Pour les Réponses Détaillées
**Utiliser**: `lmstudio-nemotron` (quand disponible)
- Temps moyen: 3.3s
- Idéal pour: Code, documentation, explications complexes

### Pour les Tests et Développement
**Utiliser**: `openclaw-wcot` ou `openclaw-dzna`
- Temps: Variable (built-in)
- Idéal pour: Tests d'agents, prototypage

## Conclusion

Les agents OpenAgents sont **fonctionnels** avec des performances acceptables :

- **Hermes-3**: Excellent pour les interactions rapides
- **Nemotron-3-Nano**: Supérieur pour les réponses détaillées malgré la latence

Le goulot principal reste le **bug de comptage de tokens** dans l'adaptateur Hermes, qui une fois corrigé permettra des mesures plus précises et une meilleure optimisation.

---

*Report généré le 9 avril 2026*
*Tests effectués avec performance-test.ps1*
