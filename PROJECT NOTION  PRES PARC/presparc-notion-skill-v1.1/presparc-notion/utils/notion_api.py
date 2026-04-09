'''
utils/notion_api.py — Wrapper API Notion avec retry et rate-limit
=================================================================
Présence-Parcours v2.0

Fonctions disponibles :
    get_database(db_id)
    update_database(db_id, payload)
    query_all_pages(db_id, filter=None, sorts=None)
    get_page(page_id)
    create_page(parent_db_id, properties, children=None)
    update_page(page_id, properties)
    archive_page(page_id)
    get_block_children(block_id)
    append_blocks(block_id, children)
    add_property(db_id, name, property_def)
    extract_title(page)
    extract_relation_ids(page, prop_name)
    make_rich_text(text)
'''

import os
import time
import logging
from typing import Any, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
NOTION_TOKEN   = os.getenv("NOTION_TOKEN", "")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
BASE_URL       = "https://api.notion.com/v1"
RATE_LIMIT_DELAY = 0.35   # secondes entre chaque requête
MAX_RETRIES      = 3
RATE_LIMIT_RETRIES = 5

logger = logging.getLogger("notion_api")


# ── Helpers privés ────────────────────────────────────────────────────────────
def _headers() -> dict[str, str]:
    if not NOTION_TOKEN:
        raise ValueError("NOTION_TOKEN non défini dans l'environnement")
    return {
        "Authorization":  f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type":   "application/json",
    }


def _request(method: str, url: str, **kwargs) -> dict:
    """
    Exécute une requête HTTP avec retry exponentiel (5xx) et
    gestion du rate-limit (429).  Ne logue jamais le token.
    """
    retry_429 = 0
    for attempt in range(MAX_RETRIES + 1):
        try:
            time.sleep(RATE_LIMIT_DELAY)
            resp = requests.request(method, url, headers=_headers(),
                                    timeout=30, **kwargs)
            if resp.status_code == 429:
                retry_429 += 1
                if retry_429 > RATE_LIMIT_RETRIES:
                    resp.raise_for_status()
                wait = float(resp.headers.get("Retry-After", 1))
                logger.warning(f"Rate-limit 429 — attente {wait}s (tentative {retry_429})")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                if attempt < MAX_RETRIES:
                    wait = 2 ** attempt
                    logger.warning(f"Erreur {resp.status_code} — retry dans {wait}s")
                    time.sleep(wait)
                    continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                logger.warning(f"Timeout — retry {attempt+1}/{MAX_RETRIES}")
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError(f"Échec après {MAX_RETRIES} tentatives : {url}")


# ── API publique ──────────────────────────────────────────────────────────────
def get_database(db_id: str) -> dict:
    return _request("GET", f"{BASE_URL}/databases/{db_id}")


def update_database(db_id: str, payload: dict) -> dict:
    return _request("PATCH", f"{BASE_URL}/databases/{db_id}", json=payload)


def query_all_pages(db_id: str,
                    filter: Optional[dict] = None,
                    sorts: Optional[list] = None) -> list[dict]:
    '''Récupère toutes les pages d'une base (pagination automatique).'''
    pages, cursor = [], None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if filter:  body["filter"]     = filter
        if sorts:   body["sorts"]      = sorts
        if cursor:  body["start_cursor"] = cursor
        data = _request("POST", f"{BASE_URL}/databases/{db_id}/query", json=body)
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return pages


def get_page(page_id: str) -> dict:
    return _request("GET", f"{BASE_URL}/pages/{page_id}")


def create_page(parent_db_id: str, properties: dict,
                children: Optional[list] = None) -> dict:
    body: dict[str, Any] = {
        "parent": {"database_id": parent_db_id},
        "properties": properties,
    }
    if children:
        body["children"] = children
    return _request("POST", f"{BASE_URL}/pages", json=body)


def update_page(page_id: str, properties: dict) -> dict:
    return _request("PATCH", f"{BASE_URL}/pages/{page_id}",
                    json={"properties": properties})


def archive_page(page_id: str) -> dict:
    return _request("PATCH", f"{BASE_URL}/pages/{page_id}",
                    json={"archived": True})


def get_block_children(block_id: str) -> list[dict]:
    data = _request("GET", f"{BASE_URL}/blocks/{block_id}/children")
    return data.get("results", [])


def append_blocks(block_id: str, children: list) -> dict:
    return _request("PATCH", f"{BASE_URL}/blocks/{block_id}/children",
                    json={"children": children})


def add_property(db_id: str, name: str, property_def: dict) -> bool:
    '''Ajoute une propriété à une base si elle n'existe pas déjà (409 = skip).'''
    try:
        update_database(db_id, {"properties": {name: property_def}})
        logger.info(f"Propriété ajoutée : {name} dans {db_id}")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 409:
            logger.info(f"Propriété déjà existante (skip) : {name}")
            return False
        raise


# ── Helpers d'extraction ──────────────────────────────────────────────────────
def extract_title(page: dict) -> str:
    '''Extrait le texte du titre d'une page Notion.'''
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            parts = prop.get("title", [])
            return "".join(p.get("plain_text", "") for p in parts)
    return ""


def extract_relation_ids(page: dict, prop_name: str) -> list[str]:
    '''Extrait les IDs d'une propriété relation.'''
    prop = page.get("properties", {}).get(prop_name, {})
    return [r["id"] for r in prop.get("relation", [])]


def make_rich_text(text: str) -> list[dict]:
    '''Crée un bloc rich_text Notion à partir d'une chaîne.'''
    return [{"type": "text", "text": {"content": str(text)}}]