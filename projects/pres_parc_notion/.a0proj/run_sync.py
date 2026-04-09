import os, yaml, sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.core.sync_engine import SyncEngine

def main():
    load_dotenv()
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)

    try:
        engine = SyncEngine(config)
        engine.run()
        print("✅ Sync terminée. Début de la regénération des portails (Dual Agent LLM)...")
        
        from agent.core.orchestrator import PresenceOrchestrator
        orch = PresenceOrchestrator()
        eleves = orch.notion.databases.query(database_id=os.environ.get("DB_BASE_ELEVES")).get("results", [])
        
        for eleve in eleves:
            props = eleve.get("properties", {})
            portail_url = props.get("Lien portail famille", {}).get("url")
            if portail_url:
                portail_id = orch.extract_id(portail_url)
                if portail_id:
                    print(f"🔄 Regénération du portail: {portail_id} ...")
                    blocks = orch.generate_seance_blocks(eleve["id"])
                    orch.clear_and_rebuild(portail_id, blocks)
                    
        print("✅ Tous les portails ont été mis à jour avec le LLM.")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()
