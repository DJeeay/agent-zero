"""
utils/logger.py — Logging structuré avec rotation de fichiers
=============================================================
Présence-Parcours v2.0

Fournit un logger standardisé pour tous les scripts du portail.
Écriture en fichier avec rotation + affichage console coloré optionnel.

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Opération réussie")
    logger.error("Erreur API 404", extra={"db": "ELEVES", "endpoint": "/pages/..."})
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration par défaut (peut être surchargée via variables d'environnement)
# ---------------------------------------------------------------------------
LOG_DIR = os.getenv("LOG_DIR", "/a0/usr/notion-agent/logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))   # 10 MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 7))             # 7 fichiers

# Fichiers de log
LOG_FILE_MAIN = os.path.join(LOG_DIR, "execution.log")
LOG_FILE_ERRORS = os.path.join(LOG_DIR, "errors.log")

# Format des messages
FORMAT_FILE = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
FORMAT_CONSOLE = "%(levelname)s  %(name)s — %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _ensure_log_dir() -> None:
    """Crée le répertoire de logs s'il n'existe pas."""
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)


def _build_file_handler(filepath: str, level: int = logging.DEBUG) -> RotatingFileHandler:
    """Crée un handler fichier avec rotation automatique."""
    _ensure_log_dir()
    handler = RotatingFileHandler(
        filepath,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(FORMAT_FILE, datefmt=DATE_FORMAT))
    return handler


def _build_console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    """Crée un handler console avec formatage simplifié."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(FORMAT_CONSOLE))
    return handler


def _build_error_file_handler() -> RotatingFileHandler:
    """Handler dédié aux erreurs critiques (ERROR + CRITICAL)."""
    handler = _build_file_handler(LOG_FILE_ERRORS, level=logging.ERROR)
    return handler


# ---------------------------------------------------------------------------
# Cache des loggers pour éviter les doublons de handlers
# ---------------------------------------------------------------------------
_loggers: dict[str, logging.Logger] = {}


def get_logger(
    name: str,
    console: bool = True,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Retourne un logger nommé, configuré avec :
    - fichier principal (execution.log) — tous niveaux >= DEBUG
    - fichier erreurs (errors.log) — ERROR et CRITICAL uniquement
    - console stdout — INFO par défaut (désactivable)

    Args:
        name: Nom du logger (généralement __name__ du module appelant)
        console: Afficher les messages en console (défaut: True)
        level: Niveau de log (DEBUG/INFO/WARNING/ERROR). Priorité sur LOG_LEVEL env.

    Returns:
        logging.Logger configuré
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    effective_level = getattr(logging, (level or LOG_LEVEL), logging.INFO)
    logger.setLevel(effective_level)

    # Éviter la propagation vers le root logger (doublons)
    logger.propagate = False

    # Handler fichier principal
    logger.addHandler(_build_file_handler(LOG_FILE_MAIN, level=logging.DEBUG))

    # Handler fichier erreurs uniquement
    logger.addHandler(_build_error_file_handler())

    # Handler console (optionnel)
    if console:
        logger.addHandler(_build_console_handler(level=effective_level))

    _loggers[name] = logger
    return logger


# ---------------------------------------------------------------------------
# Helpers pour journalisation structurée des opérations Notion
# ---------------------------------------------------------------------------

def log_api_call(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: Optional[float] = None,
) -> None:
    """
    Journalise un appel API Notion de façon structurée.
    Ne loggue jamais le token ni les données personnelles.

    Args:
        logger: Logger à utiliser
        method: HTTP method (GET, POST, PATCH, DELETE)
        endpoint: URL relative (ex: /databases/{id}/query)
        status_code: Code HTTP de la réponse
        duration_ms: Durée en millisecondes (optionnel)
    """
    level = logging.INFO if status_code < 400 else logging.ERROR
    duration_str = f" [{duration_ms:.0f}ms]" if duration_ms is not None else ""
    logger.log(
        level,
        f"API {method} {endpoint} → {status_code}{duration_str}",
    )


def log_operation(
    logger: logging.Logger,
    operation: str,
    db_name: str,
    count: int = 0,
    status: str = "OK",
    details: Optional[str] = None,
) -> None:
    """
    Journalise une opération métier (audit, génération, mise à jour).

    Args:
        logger: Logger à utiliser
        operation: Nom de l'opération (ex: "generate_monthly_report")
        db_name: Base concernée (ex: "COMPTES_RENDUS")
        count: Nombre d'éléments traités
        status: "OK" | "WARN" | "ERROR" | "SKIP"
        details: Message complémentaire (sans données personnelles)
    """
    msg = f"[{operation}] {db_name} — {count} entrées — {status}"
    if details:
        msg += f" | {details}"

    level = {
        "OK": logging.INFO,
        "SKIP": logging.INFO,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
    }.get(status.upper(), logging.INFO)

    logger.log(level, msg)


def log_session_header(logger: logging.Logger, script_name: str, mode: str = "run") -> None:
    """
    Loggue l'en-tête de démarrage d'un script.

    Args:
        logger: Logger à utiliser
        script_name: Nom du script (ex: "generate_monthly_report.py")
        mode: "dry-run" | "run" | "apply"
    """
    sep = "=" * 60
    logger.info(sep)
    logger.info(f"DÉMARRAGE : {script_name} [mode={mode}]")
    logger.info(sep)


def log_session_footer(
    logger: logging.Logger,
    script_name: str,
    created: int = 0,
    updated: int = 0,
    skipped: int = 0,
    errors: int = 0,
) -> None:
    """
    Loggue le résumé de fin d'exécution d'un script.

    Args:
        logger: Logger à utiliser
        script_name: Nom du script
        created: Nombre d'entrées créées
        updated: Nombre d'entrées mises à jour
        skipped: Nombre d'entrées ignorées (déjà existantes)
        errors: Nombre d'erreurs
    """
    status = "SUCCÈS" if errors == 0 else f"TERMINÉ AVEC {errors} ERREUR(S)"
    logger.info(
        f"FIN : {script_name} — {status} | "
        f"créés={created} mis_à_jour={updated} ignorés={skipped} erreurs={errors}"
    )
    logger.info("=" * 60)
