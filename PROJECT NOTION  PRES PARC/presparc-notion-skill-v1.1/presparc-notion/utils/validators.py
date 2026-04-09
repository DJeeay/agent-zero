'''
utils/validators.py — Validation des données avant écriture Notion
===================================================================
Présence-Parcours v2.0
'''

import re
from datetime import datetime
from typing import Any

# ── Patterns ──────────────────────────────────────────────────────────────────
_NOTION_ID_RE = re.compile(
    r'^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$',
    re.IGNORECASE
)

# ── Valeurs autorisées ────────────────────────────────────────────────────────
NIVEAUX_VALIDES = [
    "CP","CE1","CE2","CM1","CM2",
    "6ème","5ème","4ème","3ème",
    "Seconde","Première","Terminale",
    "BTS","Licence","Master","Adulte"
]
STATUTS_ELEVE   = ["Actif", "En pause", "Terminé", "Prospect"]
MATIERES_VALIDES = [
    "Mathématiques","Français","Histoire-Géographie","Sciences","Anglais",
    "Espagnol","Allemand","Physique-Chimie","SVT","Philosophie",
    "Informatique","Économie","Arts","Musique","EPS","Autre"
]
STATUTS_SEANCE  = ["Planifiée", "Réalisée", "Annulée", "Reportée"]
STATUTS_OBJECTIF = ["À démarrer", "En cours", "Atteint", "Abandonné"]
PRIORITES        = ["Haute", "Moyenne", "Basse"]


# ── Helpers ───────────────────────────────────────────────────────────────────
def is_valid_notion_id(value: str) -> bool:
    '''Vérifie qu'une chaîne est un Notion UUID valide (avec ou sans tirets).'''
    return bool(_NOTION_ID_RE.match(str(value).strip()))


def normalize_notion_id(value: str) -> str:
    '''Retourne l'UUID sans tirets (format utilisé dans les URLs Notion).'''
    return str(value).replace("-", "").strip().lower()


def is_valid_iso_date(value: str) -> bool:
    '''Vérifie le format YYYY-MM-DD.'''
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def is_valid_iso_datetime(value: str) -> bool:
    '''Vérifie le format ISO 8601 (YYYY-MM-DDTHH:MM:SSZ ou +00:00).'''
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00",
                "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            datetime.strptime(str(value), fmt)
            return True
        except (ValueError, TypeError):
            pass
    return False


# ── Validateurs de données ────────────────────────────────────────────────────
def validate_eleve(data: dict[str, Any]) -> list[str]:
    """
    Valide un dict représentant un élève.
    Retourne la liste des erreurs (vide si tout est OK).
    """
    errors: list[str] = []
    if not data.get("nom_complet", "").strip():
        errors.append("nom_complet est requis")
    statut = data.get("statut", "")
    if statut and statut not in STATUTS_ELEVE:
        errors.append(f"statut '{statut}' invalide. Valeurs: {STATUTS_ELEVE}")
    niveau = data.get("niveau_scolaire", "")
    if niveau and niveau not in NIVEAUX_VALIDES:
        errors.append(f"niveau_scolaire '{niveau}' invalide. Valeurs: {NIVEAUX_VALIDES}")
    for mat in data.get("matieres", []):
        if mat not in MATIERES_VALIDES:
            errors.append(f"matière '{mat}' invalide")
    lien = data.get("lien_portail_famille", "")
    if lien and not lien.startswith("https://"):
        errors.append("lien_portail_famille doit commencer par https://")
    return errors


def validate_seance(data: dict[str, Any]) -> list[str]:
    '''Valide un dict représentant une séance.'''
    errors: list[str] = []
    if not data.get("titre", "").strip():
        errors.append("titre est requis")
    eleve_id = data.get("eleve_id", "")
    if eleve_id and not is_valid_notion_id(str(eleve_id)):
        errors.append(f"eleve_id '{eleve_id}' n'est pas un Notion UUID valide")
    date_val = data.get("date_heure", "")
    if date_val and not (is_valid_iso_date(str(date_val)) or is_valid_iso_datetime(str(date_val))):
        errors.append(f"date_heure '{date_val}' doit être au format ISO 8601")
    duree = data.get("duree_effective_min")
    if duree is not None:
        try:
            d = int(duree)
            if not (15 <= d <= 480):
                errors.append(f"duree_effective_min={d} doit être entre 15 et 480 minutes")
        except (ValueError, TypeError):
            errors.append("duree_effective_min doit être un entier")
    statut = data.get("statut", "")
    if statut and statut not in STATUTS_SEANCE:
        errors.append(f"statut '{statut}' invalide. Valeurs: {STATUTS_SEANCE}")
    for mat in data.get("matieres_travaillees", []):
        if mat not in MATIERES_VALIDES:
            errors.append(f"matière '{mat}' invalide")
    return errors


def validate_objectif(data: dict[str, Any]) -> list[str]:
    '''Valide un dict représentant un objectif.'''
    errors: list[str] = []
    if not data.get("titre", "").strip():
        errors.append("titre est requis")
    eleve_id = data.get("eleve_id", "")
    if eleve_id and not is_valid_notion_id(str(eleve_id)):
        errors.append(f"eleve_id '{eleve_id}' n'est pas un Notion UUID valide")
    statut = data.get("statut", "")
    if statut and statut not in STATUTS_OBJECTIF:
        errors.append(f"statut '{statut}' invalide. Valeurs: {STATUTS_OBJECTIF}")
    priorite = data.get("priorite", "")
    if priorite and priorite not in PRIORITES:
        errors.append(f"priorité '{priorite}' invalide. Valeurs: {PRIORITES}")
    matiere = data.get("matiere", "")
    if matiere and matiere not in MATIERES_VALIDES:
        errors.append(f"matière '{matiere}' invalide")
    for field in ("date_debut", "date_cible"):
        val = data.get(field, "")
        if val and not is_valid_iso_date(str(val)):
            errors.append(f"{field} '{val}' doit être au format YYYY-MM-DD")
    return errors