{
  "tool_name": "memory_save",
  "tool_args": {
    "text": "Procédure : generate_monthly_report — Séquence : 1) query SEANCES filtre Mois=YYYY-MM 2) group_by Élève 3) create page COMPTES_RENDUS avec rollup séances 4) update Portail Famille",
    "metadata": {
      "area": "presparc_procedures",
      "version": "1.0",
      "type": "procedure",
      "task": "generate_monthly_report",
      "validated_by": "human",
      "date": "2026-01-04",
      "immutable": true
    }
  }
}

Règle de versionnement : une procédure avec "immutable": true n'est jamais écrasée. 
Pour modifier, l'agent crée une version 1.1 et 
marque l'ancienne "deprecated": true 
— uniquement après ta validation explicite.