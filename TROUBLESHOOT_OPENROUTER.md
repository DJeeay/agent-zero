# Guide de Dépannage - Agent Zero OpenRouter

## 📋 Résumé du Problème Résolu

**Date de résolution** : 2025-04-05  
**Problème** : Erreur d'authentification OpenRouter (401)  
**Cause** : Format incorrect de la clé API dans le fichier `.env`

---

## 🔴 Le Problème

### Symptômes
```
litellm.AuthenticationError: OpenrouterException - {"error":{"message":"Missing Authentication header","code":401}}
```

### Cause Racine
La clé API OpenRouter contenait un préfixe parasite dans le fichier `.env` :
```bash
# ❌ INCORRECT - avant correction
API_KEY_OPENROUTER=************;  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

# ✅ CORRECT - après correction
API_KEY_OPENROUTER=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
```

L'extension `memorize_solutions` ne pouvait pas s'authentifier auprès d'OpenRouter.

---

## ✅ La Solution Appliquée

### Étape 1 : Correction du fichier `.env`
**Fichier** : `@d:\DOCKER Cont 1 AZ\.env:40`

Suppression du préfixe `************;  ` avant la clé API.

### Étape 2 : Recréation du conteneur
```powershell
cd "D:\DOCKER Cont 1 AZ"
docker stop agent-zero
docker rm agent-zero
docker run -d --name agent-zero --env-file .env -p 50080:80 -v agent0-state:/app/state agent0ai/agent-zero:latest
```

### Étape 3 : Vérification
```powershell
docker exec agent-zero printenv API_KEY_OPENROUTER
# Doit afficher : sk-or-v1-... (sans préfixe)
```

---

## 🔍 Guide de Diagnostic

### Comment reconnaître ce problème ?

| Symptôme | Indication |
|----------|-----------|
| Erreur `401 Unauthorized` dans les logs | Clé API manquante ou invalide |
| Extension `memorize_solutions` échoue | Problème d'authentification OpenRouter |
| Réponse vide ou erreur dans le chat | Le LLM ne peut pas répondre |

### Vérification rapide
```powershell
# 1. Vérifier que le conteneur tourne
docker ps | findstr agent-zero

# 2. Vérifier la clé API dans le conteneur
docker exec agent-zero printenv API_KEY_OPENROUTER

# 3. Vérifier les logs récents
docker logs agent-zero --tail 20
```

---

## 🛡️ Prévention

### Règles d'or pour le fichier `.env`

1. **Format des clés API** : Toujours commencer directement par `sk-or-v1-`
2. **Pas d'espaces** : Avant ou après la clé
3. **Pas de préfixes** : Comme `************;` ou autres masquages
4. **Une seule clé** : Pas de clés multiples séparées par `;`

### ❌ Exemples à ÉVITER
```bash
# Mauvais : préfixe parasite
API_KEY_OPENROUTER=************;  sk-or-v1-...

# Mauvais : espaces
API_KEY_OPENROUTER=  sk-or-v1-...
API_KEY_OPENROUTER=sk-or-v1-...  

# Mauvais : multiples clés
API_KEY_OPENROUTER=sk-or-v1-...; sk-or-v1-...
```

### ✅ Exemple CORRECT
```bash
API_KEY_OPENROUTER=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
```

---

## 🚨 Procédure de Récupération

Si le problème revient :

### 1. Vérifier le fichier `.env`
Ouvrir `d:\DOCKER Cont 1 AZ\.env` et vérifier la ligne 40 :
- Doit commencer par `sk-or-v1-`
- Pas de caractères avant
- Pas d'espaces

### 2. Corriger si nécessaire
```powershell
# Éditer le fichier
notepad "D:\DOCKER Cont 1 AZ\.env"
```

### 3. Recréer le conteneur
```powershell
cd "D:\DOCKER Cont 1 AZ"
docker stop agent-zero
docker rm agent-zero
docker run -d --name agent-zero --env-file .env -p 50080:80 -v agent0-state:/app/state agent0ai/agent-zero:latest
```

### 4. Tester
```powershell
# Vérifier le statut
docker ps | findstr agent-zero

# Vérifier la clé
docker exec agent-zero printenv API_KEY_OPENROUTER

# Tester l'interface
curl -s http://localhost:50080/ | Select-String -Pattern "Agent Zero"
```

---

## 📊 Checklist de Validation

- [ ] Conteneur `agent-zero` en statut `Up`
- [ ] Port `50080` exposé et accessible
- [ ] `API_KEY_OPENROUTER` correctement formaté (commence par `sk-or-v1-`)
- [ ] Interface web répond sur `http://localhost:50080`
- [ ] Chat fonctionne sans erreur 401

---

## 🔗 Références

- **Fichier `.env`** : `d:\DOCKER Cont 1 AZ\.env`
- **Documentation complète** : `RAPPORT_AGENT_ZERO_AUTHENTICATION_ERROR.md`
- **Commandes rapides** : `COMMANDES_RAPIDES.md`

---

**Document créé le** : 2025-04-05  
**Version** : 1.0  
**Statut** : ✅ Solution validée et opérationnelle
