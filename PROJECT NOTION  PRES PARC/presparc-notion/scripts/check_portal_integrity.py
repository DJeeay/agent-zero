#!/usr/bin/env python3
'''
check_portal_integrity.py — Audit temps réel du workspace Notion
================================================================
Présence-Parcours v2.0

Usage:
    python scripts/check_portal_integrity.py
    python scripts/check_portal_integrity.py --json-only
    python scripts/check_portal_integrity.py --output ./output/audit.json
'''

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from utils.notion_api import get_database, query_all_pages
from utils.logger import get_logger, log_session_header, log_session_footer

logger = get_logger("check_portal_integrity")

# ── Schéma attendu ────────────────────────────────────────────────────────────
EXPECTED_SCHEMAS: dict[str, dict] = {
    "ELEVES": {
        "db_id_env": "BASE_ELEVES_DB_ID",
        "name": "BASE ELEVES",
        "required_properties": {
            "Nom complet":         "title",
            "Statut":              "select",
            "Niveau scolaire":     "select",
            "Matières":            "multi_select",
            "Prochaine séance":    "date",
            "Lien portail famille":"url",
            "Notes internes":      "rich_text",
            "Devoirs faits (%)":   "formula",
        },
    },
    "SEANCES": {
        "db_id_env": "BASE_SEANCES_DB_ID",
        "name": "BASE SEANCES",
        "required_properties": {
            "Titre séance":          "title",
            "Date et heure":         "date",
            "Durée effective (min)": "number",
            "Statut":                "select",
            "Devoirs faits":         "checkbox",
            "Mois séance":           "formula",
            "Matières travaillées":  "multi_select",
            "Contenu de la séance":  "rich_text",
            "Difficultés observées": "rich_text",
            "Points positifs":       "rich_text",
        },
    },
    "OBJECTIFS": {
        "db_id_env": "BASE_OBJECTIFS_DB_ID",
        "name": "BASE OBJECTIFS",
        "required_properties": {
            "Titre":          "title",
            "Matière":        "select",
            "Statut":         "select",
            "Priorité":       "select",
            "Progrès":        "select",
            "Date début":     "date",
            "Date cible":     "date",
            "Description":    "rich_text",
            "Actions prévues":"rich_text",
        },
    },
    "COMPTES_RENDUS": {
        "db_id_env": "BASE_COMPTES_RENDUS_DB_ID",
        "name": "BASE COMPTES RENDUS",
        "required_properties": {
            "Titre":                  "title",
            "Période":                "select",
            "Date d'envoi":           "date",
            "Évaluation globale":     "select",
            "Autonomie":              "select",
            "Points forts":           "rich_text",
            "Points à améliorer":     "rich_text",
            "Note privée enseignant": "rich_text",
            "Envoyé aux parents":     "checkbox",
            "Nb séances ce mois":     "number",
            "Taux présence (%)":      "number",
        },
    },
    "ABSENCES": {
        "db_id_env": "BASE_ABSENCES_DB_ID",
        "name": "BASE ABSENCES",
        "required_properties": {
            "Titre":     "title",
            "Date":      "date",
            "Motif":     "select",
            "Justifiée": "checkbox",
        },
    },
}


def audit_database(schema_key: str, schema: dict) -> dict:
    '''Audite une base Notion contre son schéma attendu.'''
    db_id = os.getenv(schema["db_id_env"], "")
    result: dict = {
        "name":                schema["name"],
        "db_id":               db_id or "NON DÉFINI",
        "status":              "OK",
        "missing_properties":  [],
        "wrong_types":         [],
        "broken_relations":    [],
        "entry_count":         0,
        "error":               None,
    }
    if not db_id:
        result["status"] = "ERROR"
        result["error"]  = f"Variable {schema['db_id_env']} non définie dans .env"
        return result
    try:
        db_data   = get_database(db_id)
        existing  = db_data.get("properties", {})
        result["entry_count"] = len(query_all_pages(db_id))
        for prop_name, expected_type in schema["required_properties"].items():
            if prop_name not in existing:
                result["missing_properties"].append(prop_name)
            elif existing[prop_name].get("type") != expected_type:
                result["wrong_types"].append({
                    "property": prop_name,
                    "expected": expected_type,
                    "actual":   existing[prop_name].get("type"),
                })
        if result["missing_properties"] or result["wrong_types"]:
            result["status"] = "WARN"
    except Exception as exc:
        result["status"] = "ERROR"
        result["error"]  = str(exc)
    return result


def run_audit(json_only: bool = False) -> dict:
    '''Lance l'audit complet et retourne le rapport.'''
    if not json_only:
        log_session_header(logger, "check_portal_integrity.py", "audit")
    results  = {}
    total_issues = 0
    for key, schema in EXPECTED_SCHEMAS.items():
        res = audit_database(key, schema)
        results[key] = res
        issues = len(res["missing_properties"]) + len(res["wrong_types"]) + len(res["broken_relations"])
        total_issues += issues
        if not json_only:
            icon = "✓" if res["status"] == "OK" else ("✗" if res["status"] == "ERROR" else "⚠")
            print(f"  {icon} {res['name']} — {res['entry_count']} entrées"
                  + (f" — {issues} problème(s)" if issues else ""))
    report = {
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "total_issues":  total_issues,
        "status":        "OK" if total_issues == 0 else "ISSUES",
        "databases":     results,
    }
    if not json_only:
        log_session_footer(logger, "check_portal_integrity.py",
                           errors=total_issues)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit intégrité workspace Notion")
    parser.add_argument("--json-only", action="store_true",
                        help="Sortie JSON uniquement (pour parsing automatisé)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Chemin du fichier de rapport JSON")
    args = parser.parse_args()
    report = run_audit(json_only=args.json_only)
    if args.json_only:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        if not args.json_only:
            print(f"  Rapport sauvegardé : {args.output}")
    sys.exit(0 if report["total_issues"] == 0 else 1)


if __name__ == "__main__":
    main()