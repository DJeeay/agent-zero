#!/usr/bin/env python3
"""
Wrapper avec self-healing schema intégré
Exécute la synchronisation, détecte les changements de schéma et active le safe mode si nécessaire
"""

import subprocess
import sys
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from verify_sync import SyncHealthChecker
from agent.core.schema_checker import SchemaChecker
from notion_client import Client

def run_with_self_healing():
    """Exécute l'orchestrator avec self-healing schema"""
    print("🚀 Démarrage de la synchronisation avec self-healing schema...")

    load_dotenv()
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)

    checker = SyncHealthChecker()

    # Exécution de l'orchestrator
    try:
        result = subprocess.run([
            sys.executable, "orchestrator.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)

        # Analyse de la sortie
        full_output = result.stdout + result.stderr
        report = checker.capture_console_output(full_output)
        report["metrics"]["exit_code"] = result.returncode

        # Vérifier les changements de schéma détectés
        if report["schema_changes"]:
            print(f"⚠️ Changements de schéma détectés: {len(report['schema_changes'])}")

            # Récupérer le schéma réel depuis Notion
            notion = Client(auth=os.getenv("NOTION_TOKEN"))
            schema_checker = SchemaChecker(notion, cache_dir="/tmp/schema_cache")
            db_id = config['notion']['base_eleves_id']

            try:
                new_schema = schema_checker._fetch_database_schema(db_id)
                success = checker.update_technical_memory(new_schema)
                if success:
                    print("✅ Schéma mis à jour avec succès")
                else:
                    print("❌ Erreur lors de la mise à jour du schéma")
            except Exception as e:
                print(f"❌ Impossible de récupérer le schéma Notion : {e}")

            # Activation du Safe Mode
            checker.activate_safe_mode("Changement de schéma détecté")

            if not checker.should_continue_sync():
                print("🛡️ Synchronisation interrompue pour protéger l'intégrité des données")
                report["status"] = "SAFE_MODE_INTERRUPTED"

        # Sauvegarde du rapport
        output_dir = Path("/tmp/reports")
        output_dir.mkdir(exist_ok=True)
        checker.output_dir = output_dir
        report_path = checker.save_report()

        # Affichage des résultats
        print("\n" + "="*60)
        print("RAPPORT DE SYNCHRONISATION AVEC SELF-HEALING")
        print("="*60)
        print(checker.get_summary())

        if report["schema_changes"]:
            print("\n🔄 Changements de schéma détectés:")
            for change in report["schema_changes"]:
                print(f"  • {change['type']}: {change.get('property', 'N/A')}")

        if report_path:
            print(f"\n📁 Rapport détaillé: {report_path}")

        if result.returncode != 0:
            print("\n📋 Sortie d'erreur:")
            print(result.stderr)

        return result.returncode

    except Exception as e:
        print(f"❌ Erreur critique lors de l'exécution: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_with_self_healing()
    sys.exit(exit_code)
