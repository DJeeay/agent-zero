#!/usr/bin/env python3
"""
deploy_skill.py — Script de déploiement du skill presparc-notion dans Agent Zero
=================================================================================
Présence-Parcours v2.0

Ce script copie tous les fichiers du skill dans le dossier Agent Zero approprié,
crée la structure de logs, et vérifie l'installation.

Usage:
    python deploy_skill.py --source ./presparc-notion-skill --target /a0/usr/skills/presparc-notion
    python deploy_skill.py --check   # Vérification uniquement sans copie

Prérequis:
    - Volume Docker monté sur /a0/usr
    - Python 3.9+
    - pip install python-dotenv

"""

import argparse
import os
import shutil
import sys
from pathlib import Path

# ─── Couleurs terminal ───────────────────────────────────────────────────────
GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW= "\033[93m"
CYAN  = "\033[96m"
RESET = "\033[0m"
BOLD  = "\033[1m"

def ok(msg):  print(f"  {GREEN}✓{RESET} {msg}")
def err(msg): print(f"  {RED}✗{RESET} {msg}")
def warn(msg):print(f"  {YELLOW}⚠{RESET} {msg}")
def info(msg):print(f"  {CYAN}→{RESET} {msg}")


# ─── Structure attendue du skill ────────────────────────────────────────────
REQUIRED_FILES = [
    "SKILL.md",
    "requirements.txt",
    ".env.example",
    "utils/notion_api.py",
    "utils/logger.py",
    "utils/validators.py",
    "scripts/check_portal_integrity.py",
    "scripts/generate_monthly_report.py",
    "scripts/bootstrap_schema.py",
    "scripts/enrich_objectifs_comptes_rendus.py",
    "scripts/create_portail_famille.py",
    "config/databases.json",
    "config/procedures_v1.md",
]

OPTIONAL_FILES = [
    "scripts/manage_comments.py",
    "scripts/rename_old_properties.py",
    "scripts/create_new_properties.py",
    "scripts/migrate_data.py",
    "scripts/cleanup_old_properties.py",
    "config/config.yaml",
]

LOG_DIRS = [
    "/a0/usr/notion-agent/logs",
    "/a0/usr/notion-agent/backups",
]

SKILL_DIRS = [
    "utils",
    "scripts",
    "config",
    "output",
]


def check_source(source_dir: Path) -> bool:
    """Vérifie que tous les fichiers requis existent dans le dossier source."""
    print(f"\n{BOLD}Vérification des fichiers source dans {source_dir}...{RESET}")
    all_ok = True
    for f in REQUIRED_FILES:
        path = source_dir / f
        if path.exists():
            ok(f)
        else:
            err(f"MANQUANT : {f}")
            all_ok = False
    for f in OPTIONAL_FILES:
        path = source_dir / f
        if path.exists():
            ok(f"{f} (optionnel)")
        else:
            warn(f"{f} (optionnel — absent)")
    return all_ok


def create_directories(target_dir: Path) -> None:
    """Crée les répertoires nécessaires."""
    print(f"\n{BOLD}Création des répertoires...{RESET}")
    for d in SKILL_DIRS:
        (target_dir / d).mkdir(parents=True, exist_ok=True)
        ok(f"{target_dir / d}")
    for d in LOG_DIRS:
        Path(d).mkdir(parents=True, exist_ok=True)
        ok(d)
    (target_dir / "output").mkdir(parents=True, exist_ok=True)


def copy_files(source_dir: Path, target_dir: Path) -> int:
    """Copie les fichiers depuis source vers cible. Retourne le nombre de fichiers copiés."""
    print(f"\n{BOLD}Copie des fichiers...{RESET}")
    all_files = REQUIRED_FILES + OPTIONAL_FILES
    copied = 0
    for f in all_files:
        src = source_dir / f
        dst = target_dir / f
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            ok(f"→ {dst}")
            copied += 1
    return copied


def create_env_file(target_dir: Path) -> None:
    """Vérifie ou crée le fichier .env (ne jamais écraser un .env existant)."""
    print(f"\n{BOLD}Vérification .env...{RESET}")
    env_path = target_dir / ".env"
    example_path = target_dir / ".env.example"
    if env_path.exists():
        warn(".env déjà présent — non écrasé. Vérifiez que les IDs sont à jour.")
    elif example_path.exists():
        shutil.copy2(example_path, env_path)
        warn(".env créé depuis .env.example — RENSEIGNEZ VOS VALEURS RÉELLES avant d'utiliser le skill.")
    else:
        err(".env.example absent — impossible de créer .env.")


def install_requirements(target_dir: Path) -> None:
    """Affiche la commande d'installation des dépendances."""
    print(f"\n{BOLD}Installation des dépendances...{RESET}")
    req_path = target_dir / "requirements.txt"
    if req_path.exists():
        info(f"Exécuter depuis le conteneur Agent Zero :")
        print(f"    pip install -r {req_path}")
    else:
        warn("requirements.txt absent.")


def verify_installation(target_dir: Path) -> bool:
    """Vérifie l'installation finale."""
    print(f"\n{BOLD}Vérification de l'installation...{RESET}")
    all_ok = True
    for f in REQUIRED_FILES:
        path = target_dir / f
        if path.exists():
            ok(f)
        else:
            err(f"MANQUANT après copie : {f}")
            all_ok = False
    return all_ok


def print_next_steps(target_dir: Path) -> None:
    """Affiche les étapes suivantes."""
    print(f"\n{BOLD}{CYAN}═══ ÉTAPES SUIVANTES ════════════════════════════════════{RESET}")
    steps = [
        f"Éditer {target_dir}/.env avec les valeurs réelles",
        f"pip install -r {target_dir}/requirements.txt",
        f"Test audit : python {target_dir}/scripts/check_portal_integrity.py --json-only",
        "Configurer les secrets dans Agent Zero :",
        "  §§secret(NOTION_TOKEN) = votre token Notion renouvelé",
        "  §§secret(NOTION_VERSION) = 2022-06-28",
        "  (+ les 5 IDs de bases depuis databases.json)",
        "Créer les tâches planifiées dans Agent Zero (voir scheduler_tasks.json)",
        "Exécuter le behaviour_adjustment (voir a0_behaviour_rules.json)",
    ]
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s}")
    print(f"{CYAN}══════════════════════════════════════════════════════════{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Déploie le skill presparc-notion dans Agent Zero"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("./presparc-notion-skill"),
        help="Dossier source contenant les fichiers du skill",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("/a0/usr/skills/presparc-notion"),
        help="Dossier de destination dans Agent Zero",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Vérification uniquement, sans copier",
    )
    args = parser.parse_args()

    print(f"\n{BOLD}{'═'*58}")
    print(f"  DÉPLOIEMENT SKILL presparc-notion — Présence-Parcours v2.0")
    print(f"{'═'*58}{RESET}")
    print(f"  Source : {args.source}")
    print(f"  Cible  : {args.target}")

    # Vérification source
    source_ok = check_source(args.source)
    if not source_ok:
        err("\nFichiers requis manquants. Corrigez avant de déployer.")
        sys.exit(1)

    if args.check:
        ok("\nVérification terminée. Aucune copie effectuée (--check).")
        sys.exit(0)

    # Déploiement
    create_directories(args.target)
    copied = copy_files(args.source, args.target)
    create_env_file(args.target)
    install_requirements(args.target)

    # Vérification finale
    install_ok = verify_installation(args.target)
    if install_ok:
        print(f"\n{GREEN}{BOLD}✓ Déploiement réussi — {copied} fichiers copiés{RESET}")
        print_next_steps(args.target)
    else:
        err(f"\nDéploiement incomplet. Vérifiez les erreurs ci-dessus.")
        sys.exit(1)


if __name__ == "__main__":
    main()
