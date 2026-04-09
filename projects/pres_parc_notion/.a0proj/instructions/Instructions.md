# SKILL: presparc-notion
## Version : 1.0 — validée le 2026-01-04

## RÈGLES ABSOLUES (ne jamais déroger)
1. Ne jamais modifier une propriété de schéma sans validation humaine explicite
2. Logger CHAQUE opération dans /a0/usr/notion-agent/logs/exec.log
3. En cas d'erreur API : logger + signaler + STOP. Ne pas improviser.
4. Ne jamais mémoriser le contenu pédagogique (noms, notes, observations élèves)
5. Ne jamais appeler behaviour_adjustment seul. Toujours demander validation.
6. Les procédures validées sont dans schema/procedures_v1.md — les suivre exactement.

## OPÉRATIONS DISPONIBLES
### Lecture (safe, toujours autorisée)
- query_students()         → liste d'élèves actifs
- query_sessions(month)    → séances d'un mois donné
- get_student_sessions(id) → séances d'un élève
- check_integrity()        → audit structure Notion

### Écriture (nécessite confirmation si données présentes)
- update_student_property(student_id, prop, value)
- create_session_entry(data)
- generate_monthly_report(month, year)
- manage_parent_comment(action, data)

## BASES DE DONNÉES
Voir schema/databases.json pour les IDs et schémas complets.

## EN CAS D'ERREUR
1. Logger l'erreur complète (status code, message, contexte)
2. NE PAS RÉESSAYER automatiquement plus de 2 fois
3. Signaler à l'utilisateur avec message précis
4. Mémoriser l'erreur UNIQUEMENT si elle est nouvelle :
   memory_save(area="notion_errors", type="error_log")