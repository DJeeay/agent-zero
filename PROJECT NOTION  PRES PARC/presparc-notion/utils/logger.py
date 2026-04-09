'''
utils/logger.py — Logging structuré avec rotation de fichiers
=============================================================
Présence-Parcours v2.0

Usage:
    from utils.logger import get_logger, log_operation, log_session_header
    logger = get_logger(__name__)
    logger.info("Opération réussie")
'''

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

LOG_DIR          = os.getenv("LOG_DIR", "/a0/usr/notion-agent/logs")
LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_MAX_BYTES    = int(os.getenv("LOG_MAX_BYTES",  10 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 7))

LOG_FILE_MAIN   = os.path.join(LOG_DIR, "execution.log")
LOG_FILE_ERRORS = os.path.join(LOG_DIR, "errors.log")

FORMAT_FILE    = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
FORMAT_CONSOLE = "%(levelname)-8s %(name)s — %(message)s"
DATE_FORMAT    = "%Y-%m-%dT%H:%M:%SZ"

_loggers: dict = {}


def _ensure_log_dir() -> None:
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)


def _file_handler(filepath: str, level: int = logging.DEBUG) -> RotatingFileHandler:
    _ensure_log_dir()
    h = RotatingFileHandler(filepath, maxBytes=LOG_MAX_BYTES,
                            backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    h.setLevel(level)
    h.setFormatter(logging.Formatter(FORMAT_FILE, datefmt=DATE_FORMAT))
    return h


def _console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(level)
    h.setFormatter(logging.Formatter(FORMAT_CONSOLE))
    return h


def get_logger(name: str, console: bool = True,
               level: Optional[str] = None) -> logging.Logger:
    '''Retourne un logger nommé configuré (fichier + console optionnel).'''
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    effective = getattr(logging, (level or LOG_LEVEL), logging.INFO)
    logger.setLevel(effective)
    logger.propagate = False
    logger.addHandler(_file_handler(LOG_FILE_MAIN, logging.DEBUG))
    logger.addHandler(_file_handler(LOG_FILE_ERRORS, logging.ERROR))
    if console:
        logger.addHandler(_console_handler(effective))
    _loggers[name] = logger
    return logger


def log_api_call(logger: logging.Logger, method: str, endpoint: str,
                 status_code: int, duration_ms: Optional[float] = None) -> None:
    '''Journalise un appel API Notion (jamais le token).'''
    lvl  = logging.INFO if status_code < 400 else logging.ERROR
    dur  = f" [{duration_ms:.0f}ms]" if duration_ms is not None else ""
    logger.log(lvl, f"API {method} {endpoint} → {status_code}{dur}")


def log_operation(logger: logging.Logger, operation: str, db_name: str,
                  count: int = 0, status: str = "OK",
                  details: Optional[str] = None) -> None:
    '''Journalise une opération métier sans données personnelles.'''
    msg = f"[{operation}] {db_name} — {count} entrées — {status}"
    if details:
        msg += f" | {details}"
    lvl = {"OK": logging.INFO, "SKIP": logging.INFO,
           "WARN": logging.WARNING, "ERROR": logging.ERROR}.get(status.upper(), logging.INFO)
    logger.log(lvl, msg)


def log_session_header(logger: logging.Logger, script_name: str,
                       mode: str = "run") -> None:
    sep = "=" * 60
    logger.info(sep)
    logger.info(f"DÉMARRAGE : {script_name} [mode={mode}]")
    logger.info(sep)


def log_session_footer(logger: logging.Logger, script_name: str,
                       created: int = 0, updated: int = 0,
                       skipped: int = 0, errors: int = 0) -> None:
    status = "SUCCÈS" if errors == 0 else f"TERMINÉ AVEC {errors} ERREUR(S)"
    logger.info(
        f"FIN : {script_name} — {status} | "
        f"créés={created} màj={updated} ignorés={skipped} erreurs={errors}"
    )
    logger.info("=" * 60)