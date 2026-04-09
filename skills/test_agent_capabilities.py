#!/usr/bin/env python3
"""
Test Agent Capabilities - Validation des capacités de l'agent autonome
Teste le scheduler, la mémoire, RAG et l'intégration Hermes
"""

import json
import requests
from datetime import datetime
from pathlib import Path

class AgentCapabilitiesTester:
    """Testeur des capacités Agent Zero"""
    
    def __init__(self):
        self.scheduler_file = Path("/a0/usr/scheduler/tasks.json")
        self.notion_index = Path("/a0/usr/projects/notion_technical_index.json")
        self.hermes_url = "http://llamacpp:8081/v1"
        
    def test_scheduler_capabilities(self):
        """Tester les capacités du scheduler"""
        print("🔧 TEST SCHEDULER CAPABILITIES")
        print("-" * 40)
        
        try:
            with open(self.scheduler_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = data.get('tasks', [])
            enabled_tasks = [t for t in tasks if t.get('enabled', False)]
            
            print(f"✅ Tâches configurées: {len(tasks)}")
            print(f"✅ Tâches actives: {len(enabled_tasks)}")
            
            # Analyser les types de tâches
            daily_tasks = [t for t in enabled_tasks if 'daily' in t.get('name', '').lower()]
            weekly_tasks = [t for t in enabled_tasks if 'weekly' in t.get('name', '').lower()]
            monthly_tasks = [t for t in enabled_tasks if 'monthly' in t.get('name', '').lower()]
            
            print(f"📅 Tâches quotidiennes: {len(daily_tasks)}")
            print(f"📆 Tâches hebdomadaires: {len(weekly_tasks)}")
            print(f"🗓️ Tâches mensuelles: {len(monthly_tasks)}")
            
            # Vérifier l'intégration Hermes
            hermes_tasks = [t for t in enabled_tasks if 'hermes' in t.get('name', '').lower()]
            print(f"🔮 Tâches Hermes: {len(hermes_tasks)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur scheduler: {e}")
            return False
    
    def test_rag_capabilities(self):
        """Tester les capacités RAG"""
        print("\n📚 TEST RAG CAPABILITIES")
        print("-" * 40)
        
        try:
            with open(self.notion_index, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            documents_count = len(index_data)
            print(f"✅ Documents indexés: {documents_count}")
            
            # Analyser les catégories
            categories = {}
            for doc_id, doc_data in index_data.items():
                category = doc_data.get('metadata', {}).get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            print("🏷️  Catégories disponibles:")
            for category, count in sorted(categories.items()):
                print(f"   • {category}: {count} documents")
            
            # Test de recherche simple
            notion_docs = [doc for doc in index_data.values() 
                          if doc.get('metadata', {}).get('technical_domain') == 'notion_integration']
            
            print(f"🔧 Documents techniques Notion: {len(notion_docs)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur RAG: {e}")
            return False
    
    def test_hermes_connectivity(self):
        """Tester la connectivité Hermes"""
        print("\n🔮 TEST HERMES CONNECTIVITY")
        print("-" * 40)
        
        try:
            # Test de base
            response = requests.get(f"{self.hermes_url}/models", timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Connectivité OK")
                print(f"🤖 Modèles disponibles: {len(models.get('data', []))}")
                
                if models.get('data'):
                    model = models['data'][0]
                    print(f"📝 Modèle principal: {model.get('id', 'Unknown')}")
                
                # Test de chat simple
                chat_response = requests.post(
                    f"{self.hermes_url}/chat/completions",
                    json={
                        "model": models.get('data', [{}])[0].get('id', 'Hermes-3-Llama-3.1-8B.Q4_K_M.gguf'),
                        "messages": [{"role": "user", "content": "Bonjour, teste ta réponse."}],
                        "max_tokens": 50
                    },
                    timeout=10
                )
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    response_text = chat_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    print(f"💬 Test chat: '{response_text[:50]}...' ✅")
                    return True
                else:
                    print(f"⚠️  Chat test failed: {chat_response.status_code}")
                    return False
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def test_agent_integration(self):
        """Tester l'intégration complète de l'agent"""
        print("\n🤖 TEST AGENT INTEGRATION")
        print("-" * 40)
        
        # Test 1: Vérifier que l'agent peut accéder à ses propres fichiers
        try:
            skills_dir = Path("/a0/skills")
            if skills_dir.exists():
                skill_files = list(skills_dir.glob("*.md"))
                skill_py_files = list(skills_dir.glob("*.py"))
                print(f"✅ Skills documentation: {len(skill_files)} fichiers")
                print(f"✅ Skills scripts: {len(skill_py_files)} fichiers")
            else:
                print("⚠️  Répertoire skills non trouvé")
        except Exception as e:
            print(f"❌ Erreur skills: {e}")
        
        # Test 2: Vérifier l'accès à la configuration
        try:
            config_dir = Path("/a0/usr/projects/scheduler_setup")
            if config_dir.exists():
                memory_config = config_dir / "memory_config.json"
                if memory_config.exists():
                    print(f"✅ Configuration mémoire trouvée")
                else:
                    print("⚠️  Configuration mémoire non trouvée")
        except Exception as e:
            print(f"❌ Erreur configuration: {e}")
        
        return True
    
    def run_full_test_suite(self):
        """Exécuter la suite complète de tests"""
        print("🧪 AGENT ZERO CAPABILITIES TEST SUITE")
        print("=" * 60)
        print(f"🕐 Heure de test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Exécuter tous les tests
        results = {}
        
        results['scheduler'] = self.test_scheduler_capabilities()
        results['rag'] = self.test_rag_capabilities()
        results['hermes'] = self.test_hermes_connectivity()
        results['integration'] = self.test_agent_integration()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.title():12} : {status}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 Success Rate: {success_rate:.0f}% ({passed_tests}/{total_tests})")
        
        if success_rate == 100:
            print("🟢 AGENT ZERO: FULLY OPERATIONAL! 🚀")
        elif success_rate >= 75:
            print("🟡 AGENT ZERO: MOSTLY OPERATIONAL")
        else:
            print("🔴 AGENT ZERO: NEEDS ATTENTION")
        
        print("=" * 60)
        
        return {
            'success_rate': success_rate,
            'passed': passed_tests,
            'total': total_tests,
            'details': results
        }

def main():
    """Fonction principale"""
    tester = AgentCapabilitiesTester()
    results = tester.run_full_test_suite()
    
    return results

if __name__ == "__main__":
    main()
