"""
utils/logger.py — placeholder import shim
==========================================
Ce fichier redirige les imports vers le vrai logger dans utils/logger.py
S'assurer que le PYTHONPATH inclut /a0/usr/skills/presparc-notion/
"""
# Le vrai fichier logger.py est dans utils/logger.py
# Ce fichier est un emplacement réservé pour compatibilité d'import
from utils.logger import get_logger, log_api_call, log_operation, log_session_header, log_session_footer

__all__ = ["get_logger", "log_api_call", "log_operation", "log_session_header", "log_session_footer"]
