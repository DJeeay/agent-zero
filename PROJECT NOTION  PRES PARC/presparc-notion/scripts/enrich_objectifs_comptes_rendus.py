#!/usr/bin/env python3
'''
enrich_objectifs_comptes_rendus.py — Enrichissement des bases OBJECTIFS,
COMPTES_RENDUS et ABSENCES avec les propriétés manquantes.
=======================================================================
Présence-Parcours v2.0 — À exécuter une seule fois à l'initialisation.

Usage:
    python scripts/enrich_objectifs_comptes_rendus.py --dry-run
    python scripts/enrich_objectifs_comptes_rendus.py --apply
'''

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from utils.notion_api import add_property, get_database
from utils.logger import get_logger, log_session_header, log_session_footer, log_operation

logger = get_logger("enrich_objectifs_comptes_rendus")

# ── Définitions des propriétés à ajouter ─────────────────────────────────────
ENRICHMENTS: dict[str, dict] = {
    "BASE_OBJECTIFS_DB_ID": {
        "name": "BASE OBJECTIFS",
        "properties": {
            "Matière":         {"select": {"options": [
                {"name": n} for n in ["Mathématiques","Français","Anglais",
                                      "Histoire-Géo","Sciences","Espagnol","Autre"]
            ]}},
            "Statut":          {"select": {"options": [
                {"name": n} for n in ["À démarrer","En cours","Atteint","Abandonné"]
            ]}},
            "Priorité":        {"select": {"options": [
                {"name": n} for n in ["Haute","Moyenne","Basse"]
            ]}},
            "Progrès":         {"select": {"options": [
                {"name": n} for n in ["0%","25%","50%","75%","100%"]
            ]}},
            "Date début":      {"date": {}},
            "Date cible":      {"date": {}},
            "Description":     {"rich_text": {}},
            "Actions prévues": {"rich_text": {}},
        },
    },
    "BASE_COMPTES_RENDUS_DB_ID": {
        "name": "BASE COMPTES RENDUS",
        "properties": {
            "Période":               {"select": {"options": []}},
            "Évaluation globale":    {"select": {"options": [
                {"name": n} for n in ["Excellent","Très bien","Bien","En progrès","À améliorer"]
            ]}},
            "Autonomie":             {"select": {"options": [
                {"name": n} for n in ["Très autonome","Autonome","En progression","Besoin d'encadrement"]
            ]}},
            "Date d'envoi":          {"date": {}},
            "Points forts":          {"rich_text": {}},
            "Points à améliorer":    {"rich_text": {}},
            "Note privée enseignant":{"rich_text": {}},
            "Envoyé aux parents":    {"checkbox": {}},
            "Nb séances ce mois":    {"number":   {"format": "number"}},
            "Taux présence (%)":     {"number":   {"format": "percent"}},
        },
    },
    "BASE_ABSENCES_DB_ID": {
        "name": "BASE ABSENCES",
        "properties": {
            "Motif":     {"select": {"options": [
                {"name": n} for n in ["Non justifiée","Maladie","Cas de force majeure","Autre"]
            ]}},
            "Justifiée": {"checkbox": {}},
        },
    },
}


def enrich_database(db_id_env: str, spec: dict, dry_run: bool) -> tuple[int, int, int]:
    '''Ajoute les propriétés manquantes à une base. Retourne (added, skipped, errors).'''
    db_id = os.getenv(db_id_env, "")
    if not db_id:
        logger.error(f"{db_id_env} non défini dans .env — skip")
        return 0, 0, 1
    added = skipped = errors = 0
    try:
        db_data   = get_database(db_id)
        existing  = set(db_data.get("properties", {}).keys())
    except Exception as e:
        logger.error(f"Impossible de lire {spec['name']} : {e}")
        return 0, 0, 1
    for prop_name, prop_def in spec["properties"].items():
        if prop_name in existing:
            logger.info(f"  SKIP (existant) : {prop_name}")
            skipped += 1
            continue
        if dry_run:
            print(f"    [DRY-RUN] Ajouterait : {prop_name} ({list(prop_def.keys())[0]})")
            added += 1
        else:
            try:
                add_property(db_id, prop_name, prop_def)
                added += 1
            except Exception as e:
                logger.error(f"  ERREUR ajout {prop_name} : {e}")
                errors += 1
    return added, skipped, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrichit les bases OBJECTIFS/CR/ABSENCES")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simuler sans modifier Notion")
    parser.add_argument("--apply",   action="store_true",
                        help="Appliquer les modifications")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Spécifier --dry-run ou --apply")

    mode = "dry-run" if args.dry_run else "apply"
    log_session_header(logger, "enrich_objectifs_comptes_rendus.py", mode)

    total_added = total_skipped = total_errors = 0
    for db_id_env, spec in ENRICHMENTS.items():
        print(f"\n  Base : {spec['name']}")
        a, s, e = enrich_database(db_id_env, spec, args.dry_run)
        total_added   += a
        total_skipped += s
        total_errors  += e
        log_operation(logger, "enrich", spec["name"], a + s,
                      "ERROR" if e else "OK",
                      f"ajoutés={a} ignorés={s} erreurs={e}")

    log_session_footer(logger, "enrich_objectifs_comptes_rendus.py",
                       created=total_added, skipped=total_skipped, errors=total_errors)
    if not args.dry_run:
        print("\n  → Lancez check_portal_integrity.py --json-only pour vérifier.")
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()