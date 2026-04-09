#!/usr/bin/env python3
'''
generate_monthly_report.py — Génération automatique des comptes-rendus mensuels
===============================================================================
Présence-Parcours v2.0

Usage:
    python scripts/generate_monthly_report.py --month=2026-02 --dry-run
    python scripts/generate_monthly_report.py --month=2026-02
    python scripts/generate_monthly_report.py --month=2026-02 --student-id=PAGE_ID
    python scripts/generate_monthly_report.py --month=2026-02 --force
'''

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from utils.notion_api import (
    query_all_pages, create_page, make_rich_text, extract_title
)
from utils.logger import (
    get_logger, log_session_header, log_session_footer, log_operation
)

logger = get_logger("generate_monthly_report")

ELEVES_DB_ID   = os.getenv("BASE_ELEVES_DB_ID", "")
SEANCES_DB_ID  = os.getenv("BASE_SEANCES_DB_ID", "")
CR_DB_ID       = os.getenv("BASE_COMPTES_RENDUS_DB_ID", "")


def get_active_students() -> list[dict]:
    '''Retourne les élèves actifs depuis BASE ELEVES.'''
    return query_all_pages(ELEVES_DB_ID, filter={
        "property": "Statut",
        "select":   {"equals": "Actif"},
    })


def get_sessions_for_month(student_page_id: str, year_month: str) -> list[dict]:
    '''Retourne les séances réalisées pour un élève sur un mois donné.'''
    year, month = year_month.split("-")
    first_day  = f"{year}-{month}-01"
    last_day   = f"{year}-{month}-{_last_day(int(year), int(month)):02d}"
    return query_all_pages(SEANCES_DB_ID, filter={
        "and": [
            {"property": "Élève",        "relation":  {"contains": student_page_id}},
            {"property": "Statut",       "select":    {"equals": "Réalisée"}},
            {"property": "Date et heure","date":      {"on_or_after": first_day}},
            {"property": "Date et heure","date":      {"on_or_before": last_day}},
        ]
    })


def cr_exists(student_page_id: str, period: str) -> bool:
    '''Vérifie si un CR existe déjà pour cet élève et cette période (idempotence).'''
    existing = query_all_pages(CR_DB_ID, filter={
        "and": [
            {"property": "Élève",   "relation": {"contains": student_page_id}},
            {"property": "Période", "select":   {"equals": period}},
        ]
    })
    return len(existing) > 0


def compute_stats(sessions: list[dict]) -> dict:
    '''Calcule les statistiques à partir de la liste des séances.'''
    nb       = len(sessions)
    devoirs  = sum(
        1 for s in sessions
        if s.get("properties", {}).get("Devoirs faits", {}).get("checkbox", False)
    )
    taux_dev = round((devoirs / nb) * 100) if nb > 0 else 0
    duree_total = sum(
        s.get("properties", {}).get("Durée effective (min)", {}).get("number") or 0
        for s in sessions
    )
    matieres_seen: set[str] = set()
    for s in sessions:
        for m in s.get("properties", {}).get("Matières travaillées", {}).get("multi_select", []):
            matieres_seen.add(m.get("name", ""))
    taux_presence = 100  # simplifié : toutes les séances récupérées sont "Réalisées"
    return {
        "nb_seances":       nb,
        "taux_devoirs":     taux_dev,
        "taux_presence":    taux_presence,
        "duree_totale_min": duree_total,
        "matieres":         sorted(matieres_seen),
    }


def create_cr(student_page: dict, period: str, stats: dict, dry_run: bool) -> bool:
    '''Crée un compte-rendu mensuel dans BASE COMPTES RENDUS.'''
    student_id   = student_page["id"]
    student_name = extract_title(student_page)
    month_label  = _month_label(period)
    titre        = f"CR {student_name} – {month_label}"
    if dry_run:
        print(f"    [DRY-RUN] Créerait : {titre}")
        print(f"              Séances={stats['nb_seances']}, "
              f"Présence={stats['taux_presence']}%, "
              f"Devoirs={stats['taux_devoirs']}%")
        return True
    properties = {
        "Titre":                  {"title":    make_rich_text(titre)},
        "Élève":                  {"relation": [{"id": student_id}]},
        "Période":                {"select":   {"name": period}},
        "Date d'envoi":           {"date":     {"start": datetime.now(timezone.utc).strftime("%Y-%m-%d")}},
        "Nb séances ce mois":     {"number":   stats["nb_seances"]},
        "Taux présence (%)":      {"number":   stats["taux_presence"]},
        "Envoyé aux parents":     {"checkbox": False},
        "Points forts":           {"rich_text": make_rich_text("")},
        "Points à améliorer":     {"rich_text": make_rich_text("")},
        "Note privée enseignant": {"rich_text": make_rich_text("")},
    }
    create_page(CR_DB_ID, properties)
    logger.info(f"CR créé : {titre}")
    return True


def _last_day(year: int, month: int) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]


def _month_label(period: str) -> str:
    MONTHS = {
        "01": "janvier", "02": "février", "03": "mars",     "04": "avril",
        "05": "mai",     "06": "juin",    "07": "juillet",  "08": "août",
        "09": "septembre","10": "octobre","11": "novembre", "12": "décembre",
    }
    year, month = period.split("-")
    return f"{MONTHS.get(month, month)} {year}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère les comptes-rendus mensuels Notion"
    )
    parser.add_argument("--month",      required=True,
                        help="Mois à traiter au format YYYY-MM")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Simuler sans créer")
    parser.add_argument("--force",      action="store_true",
                        help="Recréer même si CR existant")
    parser.add_argument("--student-id", default=None,
                        help="Traiter un seul élève (page_id Notion)")
    args = parser.parse_args()

    # Validation du format du mois
    try:
        datetime.strptime(args.month, "%Y-%m")
    except ValueError:
        ERR_EXIT(f"Format --month invalide : {args.month} (attendu YYYY-MM)")

    mode = "dry-run" if args.dry_run else "run"
    log_session_header(logger, "generate_monthly_report.py", mode)

    for env_var in ("BASE_ELEVES_DB_ID", "BASE_SEANCES_DB_ID", "BASE_COMPTES_RENDUS_DB_ID"):
        if not os.getenv(env_var):
            ERR_EXIT(f"Variable d'environnement manquante : {env_var}")

    students = get_active_students()
    if args.student_id:
        students = [s for s in students if s["id"].replace("-", "") == args.student_id.replace("-", "")]
    if not students:
        print("  Aucun élève actif trouvé.")
        sys.exit(0)

    print(f"  Traitement de {len(students)} élève(s) pour {args.month}")
    created = skipped = errors = 0
    for student in students:
        name = extract_title(student)
        try:
            if not args.force and cr_exists(student["id"], args.month):
                logger.info(f"CR déjà existant pour {name} – {args.month} (skip)")
                skipped += 1
                continue
            sessions = get_sessions_for_month(student["id"], args.month)
            if not sessions:
                logger.info(f"Aucune séance pour {name} – {args.month} (skip)")
                skipped += 1
                continue
            stats = compute_stats(sessions)
            if create_cr(student, args.month, stats, args.dry_run):
                created += 1
        except Exception as exc:
            logger.error(f"Erreur pour {name} : {exc}")
            errors += 1

    log_session_footer(logger, "generate_monthly_report.py",
                       created=created, skipped=skipped, errors=errors)
    sys.exit(0 if errors == 0 else 1)


def ERR_EXIT(msg: str) -> None:
    print(f"ERREUR : {msg}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()