import os
import yaml
import requests
from notion_client import Client
from dotenv import load_dotenv

def test_diagnostic():
    load_dotenv()
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)

    print("--- 🔍 PHASE 1 : Test LLM (llama.cpp) ---")
    try:
        url = f"{config['llm']['base_url']}/chat/completions"
        payload = {
            "model": config['llm']['model_name'],
            "messages": [{"role": "user", "content": "Réponds 'OK' si tu m'entends."}],
            "max_tokens": 10
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ LLM Connecté : {response.json()['choices'][0]['message']['content'].strip()}")
        else:
            print(f"❌ Erreur LLM (Code {response.status_code})")
    except Exception as e:
        print(f"❌ Connexion LLM impossible : {e}")

    print("\n--- 🔍 PHASE 2 : Test Notion API ---")
    try:
        notion = Client(auth=os.getenv("NOTION_TOKEN"))
        db_id = config['notion']['base_eleves_id']
        results = notion.databases.retrieve(database_id=db_id)
        print(f"✅ Notion Connecté : Base '{results['title'][0]['plain_text']}' trouvée.")
    except Exception as e:
        print(f"❌ Erreur Notion : {e}")

    print("\n--- 🔍 PHASE 3 : Test Écriture Logs ---")
    try:
        notion = Client(auth=os.getenv("NOTION_TOKEN"))
        log_db_id = config['notion']['teacher_databases']['comptes_rendus']
        notion.pages.create(
            parent={"database_id": log_db_id},
            properties={
                "Name": {"title": [{"text": {"content": "Test de connexion"}}]},
                "Status": {"select": {"name": "Success"}}
            }
        )
        print("✅ Log de test créé dans Notion.")
    except Exception as e:
        print(f"❌ Impossible d'écrire dans la base de logs : {e}")

if __name__ == "__main__":
    test_diagnostic()
