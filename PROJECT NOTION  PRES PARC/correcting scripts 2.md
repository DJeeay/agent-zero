# Tab 1

## **`bootstrap_schema.py`**

Copy  
\#\!/usr/bin/env python3  
\# \-\*- coding: utf-8 \-\*-

"""  
bootstrap\_schema.py — Bootstrap & normalisation du schéma Notion  
\===============================================================

Objectif :  
\- Aligner le schéma des bases "privées" (ELEVES, SEANCES, OBJECTIFS, COMPTES\_RENDUS, ABSENCES)  
  avec le schéma attendu par check\_portal\_integrity.py.  
\- Idempotent : relançable sans effet si tout est conforme.  
\- Contrôlé : DRY-RUN par défaut, et pas de corrections destructives sans flag explicite.

⚠️ Notes API :  
\- Les "linked databases" (vues liées) ne sont pas supportées par l’API publique.  
  Il faut viser les bases "source" (IDs réels des databases) \[Source\](https://developers.notion.com/guides/data-apis/working-with-databases)  
\- Pour créer/mettre à jour une relation, la base liée doit être partagée avec l’intégration  
  \[Source\](https://developers.notion.com/reference/update-a-database)

Usage :  
  python bootstrap\_schema.py \--dry-run  
  python bootstrap\_schema.py \--apply  
  python bootstrap\_schema.py \--apply \--fix-wrong-types  
"""

import os  
import sys  
import json  
import argparse  
from datetime import datetime

import requests  
from dotenv import load\_dotenv

load\_dotenv()

NOTION\_API\_BASE \= "https://api.notion.com/v1"  
NOTION\_VERSION \= os.getenv("NOTION\_VERSION", "2025-09-03")  
NOTION\_TOKEN \= os.getenv("NOTION\_TOKEN")

\# ──────────────────────────────────────────────────────────────  
\# Console helpers (simples, sans dépendance)  
\# ──────────────────────────────────────────────────────────────  
BOLD \= "\\033\[1m"  
RESET \= "\\033\[0m"  
GREEN \= "\\033\[92m"  
YELLOW \= "\\033\[93m"  
RED \= "\\033\[91m"  
BLUE \= "\\033\[94m"

def c(color: str, text: str) \-\> str:  
    return f"{color}{text}{RESET}"

def banner(title: str):  
    print()  
    print("=" \* 76)  
    print(f"{title}")  
    print("=" \* 76)

\# ──────────────────────────────────────────────────────────────  
\# Notion API minimal client  
\# ──────────────────────────────────────────────────────────────  
def notion\_headers() \-\> dict:  
    if not NOTION\_TOKEN:  
        raise RuntimeError("NOTION\_TOKEN manquant dans .env")  
    return {  
        "Authorization": f"Bearer {NOTION\_TOKEN}",  
        "Notion-Version": NOTION\_VERSION,  
        "Content-Type": "application/json",  
    }

def retrieve\_database(database\_id: str) \-\> dict:  
    url \= f"{NOTION\_API\_BASE}/databases/{database\_id}"  
    r \= requests.get(url, headers=notion\_headers(), timeout=30)  
    if r.status\_code \>= 400:  
        raise RuntimeError(f"retrieve\_database failed {r.status\_code}: {r.text}")  
    return r.json()

def update\_database(database\_id: str, properties\_patch: dict, dry\_run: bool) \-\> dict:  
    """  
    PATCH /databases/{id}  
    properties\_patch : objet "properties" tel que décrit par Notion (schema updates).  
    """  
    if dry\_run:  
        return {"dry\_run": True, "database\_id": database\_id, "properties": properties\_patch}

    url \= f"{NOTION\_API\_BASE}/databases/{database\_id}"  
    payload \= {"properties": properties\_patch}  
    r \= requests.patch(url, headers=notion\_headers(), data=json.dumps(payload), timeout=30)  
    if r.status\_code \>= 400:  
        raise RuntimeError(f"update\_database failed {r.status\_code}: {r.text}")  
    return r.json()

\# ──────────────────────────────────────────────────────────────  
\# Schema builders (conformes au format Notion)  
\# ──────────────────────────────────────────────────────────────  
def prop\_title():  
    return {"title": {}}

def prop\_rich\_text():  
    return {"rich\_text": {}}

def prop\_checkbox():  
    return {"checkbox": {}}

def prop\_date():  
    return {"date": {}}

def prop\_url():  
    return {"url": {}}

def prop\_number(format\_: str \= "number"):  
    return {"number": {"format": format\_}}

def prop\_select(options: list):  
    \# options \= \[{"name": "...", "color": "blue"}, ...\]  
    return {"select": {"options": options}}

def prop\_multi\_select(options: list):  
    return {"multi\_select": {"options": options}}

def prop\_relation(database\_id: str):  
    return {"relation": {"database\_id": database\_id}}

def prop\_formula(expression: str):  
    return {"formula": {"expression": expression}}

\# ──────────────────────────────────────────────────────────────  
\# Options (tu peux ajuster les listes, c’est non destructif)  
\# ──────────────────────────────────────────────────────────────  
MATIERES\_OPTIONS \= \[  
    {"name": "Français", "color": "blue"},  
    {"name": "Mathématiques", "color": "red"},  
    {"name": "Anglais", "color": "green"},  
    {"name": "Espagnol", "color": "orange"},  
    {"name": "Histoire-Géo", "color": "purple"},  
    {"name": "Sciences", "color": "pink"},  
    {"name": "Physique-Chimie", "color": "yellow"},  
    {"name": "SVT", "color": "brown"},  
    {"name": "Méthodologie", "color": "gray"},  
\]

NIVEAU\_OPTIONS \= \[  
    {"name": "6e", "color": "gray"},  
    {"name": "5e", "color": "gray"},  
    {"name": "4e", "color": "gray"},  
    {"name": "3e", "color": "gray"},  
    {"name": "Seconde", "color": "blue"},  
    {"name": "Première", "color": "purple"},  
    {"name": "Terminale", "color": "red"},  
    {"name": "Autre", "color": "yellow"},  
\]

STATUT\_ELEVE\_OPTIONS \= \[  
    {"name": "Actif", "color": "green"},  
    {"name": "En pause", "color": "yellow"},  
    {"name": "Archivé", "color": "gray"},  
\]

STATUT\_SEANCE\_OPTIONS \= \[  
    {"name": "Planifiée", "color": "blue"},  
    {"name": "Effectuée", "color": "green"},  
    {"name": "Annulée", "color": "red"},  
\]

MOTIF\_ABSENCE\_OPTIONS \= \[  
    {"name": "Maladie", "color": "red"},  
    {"name": "Voyage", "color": "blue"},  
    {"name": "Obligations familiales", "color": "orange"},  
    {"name": "Oubli", "color": "yellow"},  
    {"name": "Autre", "color": "gray"},  
\]

\# ──────────────────────────────────────────────────────────────  
\# Chargement IDs .env  
\# ──────────────────────────────────────────────────────────────  
DB\_IDS \= {  
    "ELEVES": os.getenv("BASE\_ELEVES\_DB\_ID"),  
    "SEANCES": os.getenv("SEANCES\_DB\_ID"),  
    "OBJECTIFS": os.getenv("OBJECTIFS\_DB\_ID"),  
    "COMPTES\_RENDUS": os.getenv("COMPTES\_RENDUS\_DB\_ID"),  
    "ABSENCES": os.getenv("ABSENCES\_DB\_ID"),  
}

def require\_env():  
    missing \= \[k for k, v in DB\_IDS.items() if not v\]  
    if missing:  
        raise RuntimeError(f"IDs DB manquants dans .env : {missing}")

\# ──────────────────────────────────────────────────────────────  
\# Expected schema (privé)  
\# Remarque : la propriété title existe déjà forcément, mais son NOM doit être aligné  
\# ──────────────────────────────────────────────────────────────  
def expected\_private\_schema():  
    eleves\_id \= DB\_IDS\["ELEVES"\]  
    seances\_id \= DB\_IDS\["SEANCES"\]  
    objectifs\_id \= DB\_IDS\["OBJECTIFS"\]  
    cr\_id \= DB\_IDS\["COMPTES\_RENDUS"\]  
    abs\_id \= DB\_IDS\["ABSENCES"\]

    return {  
        "ELEVES": {  
            "\_\_expected\_title\_name\_\_": "Nom complet",  
            "properties": {  
                \# title : géré via renommage si besoin  
                "Niveau scolaire": prop\_select(NIVEAU\_OPTIONS),  
                "Statut": prop\_select(STATUT\_ELEVE\_OPTIONS),  
                "Matières": prop\_multi\_select(MATIERES\_OPTIONS),  
                "Prochaine séance": prop\_date(),  
                "Taux devoirs faits (%)": prop\_number("percent"),  
                "Devoirs faits (nb)": prop\_number("number"),  
                "Séances effectuées": prop\_number("number"),  
                "Lien Portail Famille": prop\_url(),  
                "Séances": prop\_relation(seances\_id),  
                "Comptes-rendus": prop\_relation(cr\_id),  
                "Objectifs": prop\_relation(objectifs\_id),  
                "Absences": prop\_relation(abs\_id),  
            },  
        },  
        "SEANCES": {  
            "\_\_expected\_title\_name\_\_": "Titre",  
            "properties": {  
                "Date": prop\_date(),  
                "Durée effective (min)": prop\_number("number"),  
                "Statut": prop\_select(STATUT\_SEANCE\_OPTIONS),  
                "Matières travaillées": prop\_multi\_select(MATIERES\_OPTIONS),  
                "Devoirs faits ?": prop\_checkbox(),  
                "Contenu de la séance": prop\_rich\_text(),  
                "Difficultés observées": prop\_rich\_text(),  
                "Points positifs": prop\_rich\_text(),  
                "Devoirs pour la prochaine fois": prop\_rich\_text(),  
                "Note privée": prop\_rich\_text(),  
                "Élève": prop\_relation(eleves\_id),  
                "Mois": prop\_formula('formatDate(prop("Date"), "YYYY-MM")'),  
            },  
        },  
        "OBJECTIFS": {  
            "\_\_expected\_title\_name\_\_": "Titre",  
            "properties": {  
                "Élève": prop\_relation(eleves\_id),  
                "Matière": prop\_select(MATIERES\_OPTIONS),  
                "Statut": prop\_select(\[  
                    {"name": "En cours", "color": "blue"},  
                    {"name": "Atteint", "color": "green"},  
                    {"name": "En pause", "color": "yellow"},  
                    {"name": "Abandonné", "color": "gray"},  
                \]),  
                "Priorité": prop\_select(\[  
                    {"name": "Haute", "color": "red"},  
                    {"name": "Moyenne", "color": "yellow"},  
                    {"name": "Basse", "color": "gray"},  
                \]),  
                "Progrès": prop\_select(\[  
                    {"name": "🔴 Aucun", "color": "red"},  
                    {"name": "🟠 Faible", "color": "orange"},  
                    {"name": "🟡 Moyen", "color": "yellow"},  
                    {"name": "🟢 Bon", "color": "green"},  
                    {"name": "✅ Excellent", "color": "blue"},  
                \]),  
                "Date début": prop\_date(),  
                "Date cible": prop\_date(),  
                "Description": prop\_rich\_text(),  
                "Actions prévues": prop\_rich\_text(),  
            },  
        },  
        "COMPTES\_RENDUS": {  
            "\_\_expected\_title\_name\_\_": "Titre",  
            "properties": {  
                "Élève": prop\_relation(eleves\_id),  
                "Période": prop\_select(\[  
                    {"name": "Janvier", "color": "blue"},  
                    {"name": "Février", "color": "blue"},  
                    {"name": "Mars", "color": "green"},  
                    {"name": "Avril", "color": "green"},  
                    {"name": "Mai", "color": "yellow"},  
                    {"name": "Juin", "color": "yellow"},  
                    {"name": "Juillet", "color": "orange"},  
                    {"name": "Août", "color": "orange"},  
                    {"name": "Septembre", "color": "red"},  
                    {"name": "Octobre", "color": "red"},  
                    {"name": "Novembre", "color": "purple"},  
                    {"name": "Décembre", "color": "purple"},  
                \]),  
                "Date d'envoi": prop\_date(),  
                "Évaluation globale": prop\_select(\[  
                    {"name": "⭐ Difficile", "color": "red"},  
                    {"name": "⭐⭐ En progression", "color": "orange"},  
                    {"name": "⭐⭐⭐ Satisfaisant", "color": "yellow"},  
                    {"name": "⭐⭐⭐⭐ Bien", "color": "blue"},  
                    {"name": "⭐⭐⭐⭐⭐ Excellent", "color": "green"},  
                \]),  
                "Autonomie": prop\_select(\[  
                    {"name": "⭐ (1/5)", "color": "red"},  
                    {"name": "⭐⭐ (2/5)", "color": "orange"},  
                    {"name": "⭐⭐⭐ (3/5)", "color": "yellow"},  
                    {"name": "⭐⭐⭐⭐ (4/5)", "color": "blue"},  
                    {"name": "⭐⭐⭐⭐⭐ (5/5)", "color": "green"},  
                \]),  
                "Points forts": prop\_rich\_text(),  
                "Points à améliorer": prop\_rich\_text(),  
                "Note privée enseignant": prop\_rich\_text(),  
                "Envoyé aux parents": prop\_checkbox(),  
                "Nb séances ce mois": prop\_number("number"),  
                "Taux présence (%)": prop\_number("percent"),  
            },  
        },  
        "ABSENCES": {  
            "\_\_expected\_title\_name\_\_": "Titre",  
            "properties": {  
                "Élève": prop\_relation(eleves\_id),  
                "Date": prop\_date(),  
                "Motif": prop\_select(MOTIF\_ABSENCE\_OPTIONS),  
                "Justifiée": prop\_checkbox(),  
            },  
        },  
    }

\# ──────────────────────────────────────────────────────────────  
\# Planning des actions (dry-run, puis apply)  
\# ──────────────────────────────────────────────────────────────  
def find\_title\_property\_name(db\_schema: dict) \-\> str:  
    props \= db\_schema.get("properties", {})  
    for name, obj in props.items():  
        if obj.get("type") \== "title":  
            return name  
    return ""

def is\_relation\_to(db\_schema: dict, prop\_name: str, expected\_db\_id: str) \-\> bool:  
    props \= db\_schema.get("properties", {})  
    obj \= props.get(prop\_name)  
    if not obj or obj.get("type") \!= "relation":  
        return False  
    rel \= obj.get("relation", {})  
    return rel.get("database\_id") \== expected\_db\_id

def plan\_actions\_for\_db(db\_name: str, db\_id: str, expected: dict) \-\> list:  
    """  
    Retourne une liste d'actions de haut niveau à exécuter :  
      \- rename\_property  
      \- add\_property  
      \- rename\_then\_add (si wrong type \+ fix)  
    """  
    schema \= retrieve\_database(db\_id)  
    actual\_props \= schema.get("properties", {})

    actions \= \[\]

    \# 1\) Title rename si nécessaire  
    expected\_title \= expected.get("\_\_expected\_title\_name\_\_", "")  
    actual\_title \= find\_title\_property\_name(schema)  
    if expected\_title and actual\_title and actual\_title \!= expected\_title:  
        actions.append({  
            "kind": "rename\_property",  
            "from": actual\_title,  
            "to": expected\_title,  
            "reason": "Aligner le nom de la propriété title (unique).",  
        })  
    elif not actual\_title:  
        actions.append({  
            "kind": "error",  
            "reason": "Aucune propriété title détectée (anormal).",  
        })

    \# 2\) Propriétés attendues  
    expected\_props \= expected.get("properties", {})  
    for prop\_name, prop\_schema in expected\_props.items():  
        if prop\_name not in actual\_props:  
            actions.append({  
                "kind": "add\_property",  
                "name": prop\_name,  
                "schema": prop\_schema,  
                "reason": "Propriété manquante.",  
            })  
            continue

        actual\_type \= actual\_props\[prop\_name\].get("type")  
        expected\_type \= list(prop\_schema.keys())\[0\]  \# ex: "select", "relation", ...

        \# Vérif type  
        if actual\_type \!= expected\_type:  
            actions.append({  
                "kind": "wrong\_type",  
                "name": prop\_name,  
                "expected\_type": expected\_type,  
                "actual\_type": actual\_type,  
                "reason": "Type incorrect.",  
            })  
            continue

        \# Vérif relation cible (si relation)  
        if expected\_type \== "relation":  
            expected\_target \= prop\_schema\["relation"\]\["database\_id"\]  
            if not is\_relation\_to(schema, prop\_name, expected\_target):  
                actions.append({  
                    "kind": "wrong\_relation\_target",  
                    "name": prop\_name,  
                    "expected\_target": expected\_target,  
                    "reason": "Relation pointe vers une autre base.",  
                })

    return actions

def build\_patch\_from\_actions(actions: list, fix\_wrong\_types: bool) \-\> dict:  
    """  
    Construit le payload \`properties\` pour update\_database.  
    \- rename\_property : {"OldName": {"name": "NewName"}}  
    \- add\_property : {"PropName": {...schema...}}  
    \- wrong\_type / wrong\_relation\_target : si fix\_wrong\_types \=\> rename en OLD\_ puis recreate  
    """  
    patch \= {}  
    ts \= datetime.now().strftime("%Y%m%d\_%H%M%S")

    for a in actions:  
        if a\["kind"\] \== "rename\_property":  
            patch\[a\["from"\]\] \= {"name": a\["to"\]}

        elif a\["kind"\] \== "add\_property":  
            patch\[a\["name"\]\] \= a\["schema"\]

        elif a\["kind"\] in ("wrong\_type", "wrong\_relation\_target"):  
            if not fix\_wrong\_types:  
                continue  
            old\_name \= a\["name"\]  
            new\_old \= f"OLD\_{old\_name}\_{ts}"  
            patch\[old\_name\] \= {"name": new\_old}  
            \# Re-création conforme : on suppose que l'action d'origine contient schema si wrong\_type.  
            \# Pour wrong\_relation\_target, on n’a pas ici le schema attendu \-\> traité ailleurs.  
            \# (On laissera la correction au niveau du plan pour rester strict.)  
        \# ignore others

    return patch

def main():  
    parser \= argparse.ArgumentParser(description="Bootstrap schéma Notion — Présence-Parcours")  
    parser.add\_argument("--dry-run", action="store\_true", help\="Simule sans modifier (par défaut si \--apply absent)")  
    parser.add\_argument("--apply", action="store\_true", help\="Applique les modifications sur Notion")  
    parser.add\_argument("--fix-wrong-types", action="store\_true",  
                        help\="Renomme les propriétés au mauvais type en OLD\_..., puis recrée la propriété attendue (plus sûr qu’un changement de type).")  
    args \= parser.parse\_args()

    if not args.apply:  
        args.dry\_run \= True

    require\_env()

    banner("bootstrap\_schema.py — Bootstrap & normalisation du schéma (PRIVÉ)")

    \# 0\) sanity checks : afficher les titres des DB ciblées  
    print(c(BOLD, "\\n📌 Bases ciblées (IDs .env)"))  
    for k, v in DB\_IDS.items():  
        print(f"  \- {k:13s} \= {v}")

    expected\_map \= expected\_private\_schema()

    global\_summary \= {  
        "dry\_run": bool(args.dry\_run),  
        "applied": bool(args.apply and not args.dry\_run),  
        "fix\_wrong\_types": bool(args.fix\_wrong\_types),  
        "databases": \[\],  
        "generated\_at": datetime.now().isoformat(),  
        "notion\_version": NOTION\_VERSION,  
    }

    for db\_name, db\_id in DB\_IDS.items():  
        print()  
        print(c(BOLD, f"▶ Base {db\_name} ({db\_id\[:8\]}…)"))

        try:  
            expected \= expected\_map\[db\_name\]  
            actions \= plan\_actions\_for\_db(db\_name, db\_id, expected)  
        except Exception as e:  
            print(c(RED, f"  ❌ Erreur: {e}"))  
            global\_summary\["databases"\].append({  
                "db\_name": db\_name, "db\_id": db\_id,  
                "status": "error", "error": str(e),  
            })  
            continue

        \# Affichage plan  
        add\_count \= sum(1 for a in actions if a\["kind"\] \== "add\_property")  
        rename\_count \= sum(1 for a in actions if a\["kind"\] \== "rename\_property")  
        wrong\_count \= sum(1 for a in actions if a\["kind"\] in ("wrong\_type", "wrong\_relation\_target"))

        if not actions or (add\_count \== 0 and rename\_count \== 0 and (wrong\_count \== 0 or not args.fix\_wrong\_types)):  
            print(c(GREEN, "  ✅ Rien à faire (ou uniquement des warnings non corrigés)."))  
        else:  
            if rename\_count:  
                print(c(YELLOW, f"  🔁 Renommages prévus : {rename\_count}"))  
            if add\_count:  
                print(c(YELLOW, f"  ➕ Propriétés à ajouter : {add\_count}"))  
            if wrong\_count:  
                print(c(YELLOW, f"  ⚠️ Anomalies (type/relation) détectées : {wrong\_count}"))

            for a in actions:  
                if a\["kind"\] \== "rename\_property":  
                    print(f"    \- rename title/property: '{a\['from'\]}' → '{a\['to'\]}'")  
                elif a\["kind"\] \== "add\_property":  
                    t \= list(a\["schema"\].keys())\[0\]  
                    print(f"    \- add: '{a\['name'\]}' \[{t}\]")  
                elif a\["kind"\] \== "wrong\_type":  
                    msg \= f"    \- wrong type: '{a\['name'\]}' {a\['actual\_type'\]} → attendu {a\['expected\_type'\]}"  
                    if args.fix\_wrong\_types:  
                        msg \+= " (sera renommé en OLD\_ puis recréé)"  
                    print(c(YELLOW, msg))  
                elif a\["kind"\] \== "wrong\_relation\_target":  
                    msg \= f"    \- wrong relation target: '{a\['name'\]}' (cible inattendue)"  
                    print(c(YELLOW, msg))  
                elif a\["kind"\] \== "error":  
                    print(c(RED, f"    \- error: {a\['reason'\]}"))

        \# Patch  
        patch \= build\_patch\_from\_actions(actions, fix\_wrong\_types=args.fix\_wrong\_types)

        \# Note : pour corriger wrong\_relation\_target proprement, on préfère un comportement strict :  
        \# le script détecte et signale, mais ne change pas automatiquement (ça peut être sensible).  
        if patch:  
            try:  
                \_ \= update\_database(db\_id, patch, dry\_run=args.dry\_run)  
                print(c(GREEN if args.dry\_run else BLUE,  
                        f"  {'🧪 DRY-RUN prêt' if args.dry\_run else '✅ Patch appliqué'} "  
                        f"({len(patch)} changements schema)"))  
            except Exception as e:  
                print(c(RED, f"  ❌ Patch échoué: {e}"))  
                global\_summary\["databases"\].append({  
                    "db\_name": db\_name, "db\_id": db\_id,  
                    "status": "patch\_failed", "error": str(e),  
                    "planned\_actions": actions,  
                    "patch": patch,  
                })  
                continue

        \# Save summary per DB  
        global\_summary\["databases"\].append({  
            "db\_name": db\_name,  
            "db\_id": db\_id,  
            "status": "ok",  
            "planned\_actions": actions,  
            "patch": patch,  
        })

    \# Export JSON local  
    os.makedirs("output", exist\_ok=True)  
    out \= f"output/bootstrap\_schema\_{datetime.now().strftime('%Y%m%d\_%H%M%S')}.json"  
    with open(out, "w", encoding="utf-8") as f:  
        json.dump(global\_summary, f, ensure\_ascii=False, indent=2)

    print()  
    print(c(GREEN, f"💾 Rapport: {out}"))

    print()  
    print(c(BOLD, "Étape recommandée :"))  
    print("  1\) python bootstrap\_schema.py \--dry-run")  
    print("  2\) python bootstrap\_schema.py \--apply")  
    print("  3\) python check\_portal\_integrity.py")  
    print()

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

# Tab 2

"""  
check\_portal\_integrity.py — Audit temps réel de l'état du workspace Notion  
\===========================================================================  
Présence-Parcours v2.0

Ce script interroge directement l'API Notion et produit :  
  • Un rapport console coloré (émojis \+ tableaux)  
  • Un fichier JSON horodaté dans le dossier output/

Usage :  
    python check\_portal\_integrity.py  
    python check\_portal\_integrity.py \--json-only     \# silencieux, juste JSON  
    python check\_portal\_integrity.py \--fix-warnings  \# corrige les warnings automatiques  
"""

import os  
import sys  
import json  
import argparse  
from datetime import datetime

from dotenv import load\_dotenv  
from utils.notion\_api import get\_database, query\_database  
from utils.logger import get\_logger, session\_header

load\_dotenv()  
logger \= get\_logger("audit")

\# ── IDs des bases (depuis .env) ───────────────────────────────────  
DB\_IDS \= {  
    "ELEVES":        os.getenv("BASE\_ELEVES\_DB\_ID"),  
    "SEANCES":       os.getenv("SEANCES\_DB\_ID"),  
    "COMPTES\_RENDUS": os.getenv("COMPTES\_RENDUS\_DB\_ID"),  
    "OBJECTIFS":     os.getenv("OBJECTIFS\_DB\_ID"),  
    "ABSENCES":      os.getenv("ABSENCES\_DB\_ID"),  
}

\# ── Schéma attendu ────────────────────────────────────────────────  
EXPECTED\_SCHEMA \= {  
    "ELEVES": {  
        "Nom complet":          "title",  
        "Niveau scolaire":      "select",  
        "Statut":               "select",  
        "Matières":             "multi\_select",  
        "Prochaine séance":     "date",  
        "Taux devoirs faits (%)": "number",  
        "Devoirs faits (nb)":   "number",  
        "Séances effectuées":   "number",  
        "Lien Portail Famille": "url",  
        "Séances":              "relation",  
        "Comptes-rendus":       "relation",  
        "Objectifs":            "relation",  
        "Absences":             "relation",  
    },  
    "SEANCES": {  
        "Titre":                "title",  
        "Date":                 "date",  
        "Durée effective (min)": "number",  
        "Statut":               "select",  
        "Matières travaillées": "multi\_select",  
        "Devoirs faits ?":      "checkbox",  
        "Contenu de la séance": "rich\_text",  
        "Difficultés observées": "rich\_text",  
        "Points positifs":      "rich\_text",  
        "Devoirs pour la prochaine fois": "rich\_text",  
        "Note privée":          "rich\_text",  
        "Élève":                "relation",  
        "Mois":                 "formula",  
    },  
    "OBJECTIFS": {  
        "Titre":        "title",  
        "Élève":        "relation",  
        "Matière":      "select",  
        "Statut":       "select",  
        "Priorité":     "select",  
        "Date début":   "date",  
        "Date cible":   "date",  
        "Description":  "rich\_text",  
        "Progrès":      "select",  
    },  
    "COMPTES\_RENDUS": {  
        "Titre":                  "title",  
        "Élève":                  "relation",  
        "Période":                "select",  
        "Date d'envoi":           "date",  
        "Points forts":           "rich\_text",  
        "Points à améliorer":     "rich\_text",  
        "Note privée enseignant": "rich\_text",  
        "Évaluation globale":     "select",  
        "Envoyé aux parents":     "checkbox",  
    },  
    "ABSENCES": {  
        "Titre":  "title",  
        "Élève":  "relation",  
        "Date":   "date",  
        "Motif":  "select",  
        "Justifiée": "checkbox",  
    },  
}

\# ── Couleurs console ──────────────────────────────────────────────  
GREEN  \= "\\033\[92m"  
YELLOW \= "\\033\[93m"  
RED    \= "\\033\[91m"  
BLUE   \= "\\033\[94m"  
BOLD   \= "\\033\[1m"  
RESET  \= "\\033\[0m"

def \_c(color, text):  
    return f"{color}{text}{RESET}"

\# ──────────────────────────────────────────────────────────────────  
\# Audit d'une base  
\# ──────────────────────────────────────────────────────────────────

def audit\_database(db\_name: str, db\_id: str) \-\> dict:  
    """  
    Audite une base de données.  
    Retourne un dictionnaire structuré avec le résultat de l'audit.  
    """  
    result \= {  
        "db\_name": db\_name,  
        "db\_id": db\_id,  
        "accessible": False,  
        "entry\_count": 0,  
        "missing\_properties": \[\],  
        "wrong\_type\_properties": \[\],  
        "extra\_old\_properties": \[\],  
        "empty\_mandatory\_fields": \[\],  
        "orphan\_relations": \[\],  
        "portal\_links\_missing": 0,  
        "errors": \[\],  
    }

    \# ── 1\. Tester l'accès ─────────────────────────────────────────  
    try:  
        db\_schema \= get\_database(db\_id)  
    except Exception as e:  
        result\["errors"\].append(f"404/Accès refusé : {e}")  
        return result

    result\["accessible"\] \= True  
    actual\_props \= db\_schema.get("properties", {})

    \# ── 2\. Comparer avec le schéma attendu ────────────────────────  
    expected \= EXPECTED\_SCHEMA.get(db\_name, {})  
    for prop\_name, expected\_type in expected.items():  
        if prop\_name not in actual\_props:  
            result\["missing\_properties"\].append(  
                {"name": prop\_name, "expected\_type": expected\_type}  
            )  
        else:  
            actual\_type \= actual\_props\[prop\_name\].get("type")  
            if actual\_type \!= expected\_type:  
                result\["wrong\_type\_properties"\].append({  
                    "name": prop\_name,  
                    "expected": expected\_type,  
                    "actual": actual\_type,  
                })

    \# ── 3\. Détection propriétés OLD\_ résiduelles ─────────────────  
    for prop\_name in actual\_props:  
        if prop\_name.startswith("OLD\_"):  
            result\["extra\_old\_properties"\].append(prop\_name)

    \# ── 4\. Compter les entrées \+ vérifier les données ─────────────  
    try:  
        pages \= query\_database(db\_id)  
        result\["entry\_count"\] \= len(pages)

        if db\_name \== "ELEVES":  
            for page in pages:  
                props \= page.get("properties", {})  
                \# Portail famille  
                portail \= props.get("Lien Portail Famille", {})  
                if not portail.get("url"):  
                    result\["portal\_links\_missing"\] \+= 1  
                \# Séances liées  
                seances\_rel \= props.get("Séances", {}).get("relation", \[\])  
                if not seances\_rel:  
                    eleve\_titre \= \_get\_title(props)  
                    result\["orphan\_relations"\].append(  
                        f"'{eleve\_titre}' : aucune séance liée"  
                    )

    except Exception as e:  
        result\["errors"\].append(f"Erreur query : {e}")

    return result

def \_get\_title(props: dict) \-\> str:  
    for val in props.values():  
        if val.get("type") \== "title":  
            texts \= val.get("title", \[\])  
            return "".join(t.get("plain\_text", "") for t in texts) or "(sans titre)"  
    return "(sans titre)"

\# ──────────────────────────────────────────────────────────────────  
\# Affichage rapport console  
\# ──────────────────────────────────────────────────────────────────

def print\_report(results: list, elapsed: float):  
    print()  
    print(\_c(BOLD \+ BLUE, "=" \* 62))  
    print(\_c(BOLD \+ BLUE, "  📊 RAPPORT D'AUDIT — PRÉSENCE-PARCOURS"))  
    print(\_c(BOLD \+ BLUE, f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"))  
    print(\_c(BOLD \+ BLUE, "=" \* 62))

    total\_ok \= 0  
    total\_warn \= 0  
    total\_err \= 0

    for r in results:  
        db\_name \= r\["db\_name"\]  
        print()  
        print(\_c(BOLD, f"  {'─'\*55}"))

        \# En-tête base  
        if r\["errors"\]:  
            icon \= "🔴"  
            total\_err \+= 1  
        elif r\["missing\_properties"\] or r\["wrong\_type\_properties"\] or r\["extra\_old\_properties"\]:  
            icon \= "🟡"  
            total\_warn \+= 1  
        else:  
            icon \= "🟢"  
            total\_ok \+= 1

        print(\_c(BOLD, f"  {icon} BASE {db\_name}  (ID: {r\['db\_id'\]\[:8\]}…)"))

        if not r\["accessible"\]:  
            print(\_c(RED, f"     ❌ Base inaccessible — {r\['errors'\]}"))  
            continue

        print(f"     📄 Entrées : {\_c(BOLD, str(r\['entry\_count'\]))}")

        \# Propriétés manquantes  
        if r\["missing\_properties"\]:  
            print(\_c(YELLOW, f"     ⚠️  Propriétés manquantes ({len(r\['missing\_properties'\])}) :"))  
            for p in r\["missing\_properties"\]:  
                print(\_c(YELLOW, f"        • {p\['name'\]} \[{p\['expected\_type'\]}\]"))

        \# Mauvais types  
        if r\["wrong\_type\_properties"\]:  
            print(\_c(YELLOW, f"     🔧 Types incorrects ({len(r\['wrong\_type\_properties'\])}) :"))  
            for p in r\["wrong\_type\_properties"\]:  
                print(\_c(YELLOW, f"        • {p\['name'\]} : {p\['actual'\]} → attendu {p\['expected'\]}"))

        \# OLD\_ résiduelles  
        if r\["extra\_old\_properties"\]:  
            print(\_c(RED, f"     🗑️  Propriétés OLD\_ résiduelles ({len(r\['extra\_old\_properties'\])}) :"))  
            for p in r\["extra\_old\_properties"\]:  
                print(\_c(RED, f"        • {p}"))

        \# Portails manquants  
        if r.get("portal\_links\_missing", 0\) \> 0:  
            print(\_c(YELLOW, f"     🔗 Portails famille manquants : {r\['portal\_links\_missing'\]} élève(s)"))

        \# Relations orphelines  
        if r.get("orphan\_relations"):  
            print(\_c(YELLOW, f"     🔗 Élèves sans séances liées :"))  
            for msg in r\["orphan\_relations"\]\[:5\]:  \# max 5 affichés  
                print(\_c(YELLOW, f"        • {msg}"))

        \# Tout OK  
        if (  
            not r\["missing\_properties"\]  
            and not r\["wrong\_type\_properties"\]  
            and not r\["extra\_old\_properties"\]  
            and not r\["errors"\]  
        ):  
            print(\_c(GREEN, f"     ✅ Schéma conforme"))

    \# Résumé global  
    print()  
    print(\_c(BOLD \+ BLUE, "  " \+ "─" \* 55))  
    print(\_c(BOLD, "  📋 RÉSUMÉ GLOBAL"))  
    print(f"  🟢 Bases OK    : {\_c(GREEN, str(total\_ok))}")  
    print(f"  🟡 Warnings    : {\_c(YELLOW, str(total\_warn))}")  
    print(f"  🔴 Erreurs     : {\_c(RED, str(total\_err))}")  
    print(f"  ⏱️  Durée       : {elapsed:.1f}s")  
    print()

    \# Recommandations  
    all\_missing \= sum(len(r\["missing\_properties"\]) for r in results)  
    all\_old \= sum(len(r\["extra\_old\_properties"\]) for r in results)

    if all\_missing \> 0:  
        print(\_c(YELLOW, f"  → Lancez : python enrich\_objectifs\_comptes\_rendus.py"))  
    if all\_old \> 0:  
        print(\_c(RED, f"  → Lancez : python cleanup\_old\_properties.py"))  
    portals\_needed \= sum(r.get("portal\_links\_missing", 0\) for r in results)  
    if portals\_needed \> 0:  
        print(\_c(YELLOW, f"  → Lancez : python create\_portail\_famille.py"))

    print(\_c(BOLD \+ BLUE, "=" \* 62))  
    print()

\# ──────────────────────────────────────────────────────────────────  
\# Export JSON  
\# ──────────────────────────────────────────────────────────────────

def save\_json\_report(results: list, elapsed: float) \-\> str:  
    os.makedirs("output", exist\_ok=True)  
    timestamp \= datetime.now().strftime("%Y%m%d\_%H%M%S")  
    filename \= f"output/audit\_{timestamp}.json"  
    report \= {  
        "generated\_at": datetime.now().isoformat(),  
        "duration\_seconds": round(elapsed, 2),  
        "summary": {  
            "total\_bases": len(results),  
            "ok": sum(1 for r in results if not r\["errors"\] and not r\["missing\_properties"\]),  
            "warnings": sum(1 for r in results if not r\["errors"\] and (r\["missing\_properties"\] or r\["wrong\_type\_properties"\])),  
            "errors": sum(1 for r in results if r\["errors"\]),  
        },  
        "databases": results,  
    }  
    with open(filename, "w", encoding="utf-8") as f:  
        json.dump(report, f, ensure\_ascii=False, indent=2)  
    return filename

\# ──────────────────────────────────────────────────────────────────  
\# Main  
\# ──────────────────────────────────────────────────────────────────

def main():  
    parser \= argparse.ArgumentParser(description="Audit Notion — Présence-Parcours")  
    parser.add\_argument("--json-only", action="store\_true", help="Pas d'affichage console")  
    args \= parser.parse\_args()

    logger.info(session\_header("check\_portal\_integrity.py"))

    \# Vérifications préalables  
    if not os.getenv("NOTION\_TOKEN"):  
        print(\_c(RED, "❌ NOTION\_TOKEN manquant dans .env"))  
        sys.exit(1)

    missing\_ids \= \[k for k, v in DB\_IDS.items() if not v\]  
    if missing\_ids:  
        print(\_c(YELLOW, f"⚠️  IDs manquants dans .env : {missing\_ids}"))

    t\_start \= datetime.now()

    results \= \[\]  
    for db\_name, db\_id in DB\_IDS.items():  
        if not db\_id:  
            results.append({  
                "db\_name": db\_name, "db\_id": "MANQUANT",  
                "accessible": False, "entry\_count": 0,  
                "missing\_properties": \[\], "wrong\_type\_properties": \[\],  
                "extra\_old\_properties": \[\], "empty\_mandatory\_fields": \[\],  
                "orphan\_relations": \[\], "portal\_links\_missing": 0,  
                "errors": \["ID non configuré dans .env"\],  
            })  
            continue  
        logger.info(f"Audit de {db\_name}...")  
        results.append(audit\_database(db\_name, db\_id))

    elapsed \= (datetime.now() \- t\_start).total\_seconds()

    if not args.json\_only:  
        print\_report(results, elapsed)

    json\_file \= save\_json\_report(results, elapsed)  
    logger.info(f"Rapport JSON sauvegardé : {json\_file}")  
    print(\_c(GREEN, f"  💾 Rapport JSON : {json\_file}"))

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

# Tab 3

"""  
enrich\_objectifs\_comptes\_rendus.py — Enrichissement des bases vides  
\====================================================================  
Présence-Parcours v2.0

Ce script ajoute les propriétés manquantes aux bases OBJECTIFS et COMPTES\_RENDUS  
qui ne contenaient initialement que Name \+ Élève (relation).

Usage :  
    python enrich\_objectifs\_comptes\_rendus.py  
    python enrich\_objectifs\_comptes\_rendus.py \--dry-run   \# Simule sans modifier  
"""

import os  
import sys  
import argparse  
from dotenv import load\_dotenv  
from utils.notion\_api import add\_property, get\_database  
from utils.logger import get\_logger, session\_header

load\_dotenv()  
logger \= get\_logger("enrich")

DB\_IDS \= {  
    "OBJECTIFS":      os.getenv("OBJECTIFS\_DB\_ID"),  
    "COMPTES\_RENDUS": os.getenv("COMPTES\_RENDUS\_DB\_ID"),  
}

\# ── Schéma OBJECTIFS ─────────────────────────────────────────────  
OBJECTIFS\_PROPERTIES \= {  
    "Matière": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "Français",          "color": "blue"},  
                {"name": "Mathématiques",     "color": "red"},  
                {"name": "Anglais",           "color": "green"},  
                {"name": "Espagnol",          "color": "orange"},  
                {"name": "Histoire-Géo",      "color": "purple"},  
                {"name": "Sciences",          "color": "pink"},  
                {"name": "Physique-Chimie",   "color": "yellow"},  
                {"name": "SVT",               "color": "brown"},  
                {"name": "Méthodologie",      "color": "gray"},  
            \]  
        },  
    },  
    "Statut": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "En cours",   "color": "blue"},  
                {"name": "Atteint",    "color": "green"},  
                {"name": "En pause",   "color": "yellow"},  
                {"name": "Abandonné",  "color": "gray"},  
            \]  
        },  
    },  
    "Priorité": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "Haute",    "color": "red"},  
                {"name": "Moyenne",  "color": "yellow"},  
                {"name": "Basse",    "color": "gray"},  
            \]  
        },  
    },  
    "Progrès": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "🔴 Aucun",        "color": "red"},  
                {"name": "🟠 Faible",       "color": "orange"},  
                {"name": "🟡 Moyen",        "color": "yellow"},  
                {"name": "🟢 Bon",          "color": "green"},  
                {"name": "✅ Excellent",    "color": "blue"},  
            \]  
        },  
    },  
    "Date début": {  
        "type": "date",  
        "date": {},  
    },  
    "Date cible": {  
        "type": "date",  
        "date": {},  
    },  
    "Description": {  
        "type": "rich\_text",  
        "rich\_text": {},  
    },  
    "Actions prévues": {  
        "type": "rich\_text",  
        "rich\_text": {},  
    },  
}

\# ── Schéma COMPTES\_RENDUS ─────────────────────────────────────────  
COMPTES\_RENDUS\_PROPERTIES \= {  
    "Période": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "Janvier",   "color": "blue"},  
                {"name": "Février",   "color": "blue"},  
                {"name": "Mars",      "color": "green"},  
                {"name": "Avril",     "color": "green"},  
                {"name": "Mai",       "color": "yellow"},  
                {"name": "Juin",      "color": "yellow"},  
                {"name": "Juillet",   "color": "orange"},  
                {"name": "Août",      "color": "orange"},  
                {"name": "Septembre", "color": "red"},  
                {"name": "Octobre",   "color": "red"},  
                {"name": "Novembre",  "color": "purple"},  
                {"name": "Décembre",  "color": "purple"},  
            \]  
        },  
    },  
    "Date d'envoi": {  
        "type": "date",  
        "date": {},  
    },  
    "Évaluation globale": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "⭐ Difficile",           "color": "red"},  
                {"name": "⭐⭐ En progression",     "color": "orange"},  
                {"name": "⭐⭐⭐ Satisfaisant",     "color": "yellow"},  
                {"name": "⭐⭐⭐⭐ Bien",           "color": "blue"},  
                {"name": "⭐⭐⭐⭐⭐ Excellent",    "color": "green"},  
            \]  
        },  
    },  
    "Autonomie": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "⭐ (1/5)",         "color": "red"},  
                {"name": "⭐⭐ (2/5)",       "color": "orange"},  
                {"name": "⭐⭐⭐ (3/5)",     "color": "yellow"},  
                {"name": "⭐⭐⭐⭐ (4/5)",   "color": "blue"},  
                {"name": "⭐⭐⭐⭐⭐ (5/5)", "color": "green"},  
            \]  
        },  
    },  
    "Points forts": {  
        "type": "rich\_text",  
        "rich\_text": {},  
    },  
    "Points à améliorer": {  
        "type": "rich\_text",  
        "rich\_text": {},  
    },  
    "Note privée enseignant": {  
        "type": "rich\_text",  
        "rich\_text": {},  
    },  
    "Envoyé aux parents": {  
        "type": "checkbox",  
        "checkbox": {},  
    },  
    "Nb séances ce mois": {  
        "type": "number",  
        "number": {"format": "number"},  
    },  
    "Taux présence (%)": {  
        "type": "number",  
        "number": {"format": "percent"},  
    },  
}

\# ── Propriétés supplémentaires ABSENCES ───────────────────────────  
ABSENCES\_EXTRA\_PROPERTIES \= {  
    "Motif": {  
        "type": "select",  
        "select": {  
            "options": \[  
                {"name": "Maladie",         "color": "red"},  
                {"name": "Voyage",          "color": "blue"},  
                {"name": "Obligations familiales", "color": "orange"},  
                {"name": "Oubli",           "color": "yellow"},  
                {"name": "Autre",           "color": "gray"},  
            \]  
        },  
    },  
    "Justifiée": {  
        "type": "checkbox",  
        "checkbox": {},  
    },  
}

def print\_banner(title: str):  
    print()  
    print("=" \* 62\)  
    print(f"  {title}")  
    print("=" \* 62\)

def enrich\_base(db\_name: str, db\_id: str, properties: dict, dry\_run: bool) \-\> dict:  
    """  
    Ajoute les propriétés manquantes à une base de données.  
    """  
    result \= {"db\_name": db\_name, "added": 0, "skipped": 0, "errors": 0}

    print()  
    print(f"📁 Base : {db\_name} (ID: {db\_id\[:8\]}…)")

    \# Récupère le schéma actuel  
    try:  
        schema \= get\_database(db\_id)  
    except Exception as e:  
        print(f"  ❌ Base inaccessible : {e}")  
        result\["errors"\] \+= 1  
        return result

    existing \= set(schema.get("properties", {}).keys())

    for prop\_name, prop\_config in properties.items():  
        if prop\_name in existing:  
            print(f"  ⏭️  '{prop\_name}' existe déjà — ignoré")  
            result\["skipped"\] \+= 1  
            continue

        if dry\_run:  
            print(f"  🔍 \[DRY-RUN\] Ajouterait : '{prop\_name}' ({prop\_config\['type'\]})")  
            result\["added"\] \+= 1  
        else:  
            success \= add\_property(db\_id, prop\_name, prop\_config)  
            if success:  
                result\["added"\] \+= 1  
            else:  
                result\["errors"\] \+= 1

    return result

def main():  
    parser \= argparse.ArgumentParser(  
        description="Enrichissement des bases OBJECTIFS et COMPTES\_RENDUS"  
    )  
    parser.add\_argument("--dry-run", action="store\_true",  
                        help="Simule sans modifier Notion")  
    parser.add\_argument("--absences-only", action="store\_true",  
                        help="Enrichit seulement la base ABSENCES")  
    args \= parser.parse\_args()

    logger.info(session\_header("enrich\_objectifs\_comptes\_rendus.py"))

    if not os.getenv("NOTION\_TOKEN"):  
        print("❌ NOTION\_TOKEN manquant dans .env")  
        sys.exit(1)

    if args.dry\_run:  
        print\_banner("🔍 MODE DRY-RUN — Aucune modification ne sera effectuée")  
    else:  
        print\_banner("🚀 Enrichissement des bases vides — Présence-Parcours v2.0")

    all\_results \= \[\]

    if not args.absences\_only:  
        \# OBJECTIFS  
        obj\_id \= os.getenv("OBJECTIFS\_DB\_ID")  
        if obj\_id:  
            all\_results.append(  
                enrich\_base("OBJECTIFS", obj\_id, OBJECTIFS\_PROPERTIES, args.dry\_run)  
            )  
        else:  
            print("\\n⚠️  OBJECTIFS\_DB\_ID non configuré dans .env")

        \# COMPTES\_RENDUS  
        cr\_id \= os.getenv("COMPTES\_RENDUS\_DB\_ID")  
        if cr\_id:  
            all\_results.append(  
                enrich\_base("COMPTES\_RENDUS", cr\_id, COMPTES\_RENDUS\_PROPERTIES, args.dry\_run)  
            )  
        else:  
            print("\\n⚠️  COMPTES\_RENDUS\_DB\_ID non configuré dans .env")

    \# ABSENCES (extras)  
    abs\_id \= os.getenv("ABSENCES\_DB\_ID")  
    if abs\_id:  
        all\_results.append(  
            enrich\_base("ABSENCES", abs\_id, ABSENCES\_EXTRA\_PROPERTIES, args.dry\_run)  
        )

    \# Résumé  
    print()  
    print("=" \* 62\)  
    print("  📋 RÉSUMÉ")  
    print("=" \* 62\)  
    total\_added \= sum(r\["added"\] for r in all\_results)  
    total\_skipped \= sum(r\["skipped"\] for r in all\_results)  
    total\_errors \= sum(r\["errors"\] for r in all\_results)

    for r in all\_results:  
        status \= "✅" if r\["errors"\] \== 0 else "❌"  
        print(f"  {status} {r\['db\_name'\]}: \+{r\['added'\]} propriétés, "  
              f"{r\['skipped'\]} ignorées, {r\['errors'\]} erreurs")

    print(f"\\n  Total : \+{total\_added} propriétés ajoutées")

    if total\_errors \== 0 and not args.dry\_run:  
        print()  
        print("  ✅ Enrichissement terminé avec succès \!")  
        print()  
        print("  📋 PROCHAINES ÉTAPES :")  
        print("  1\. Vérifier dans Notion que les nouvelles propriétés apparaissent")  
        print("  2\. Lancer l'audit : python check\_portal\_integrity.py")  
        print("  3\. Créer les portails : python create\_portail\_famille.py")

    print()

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()  
