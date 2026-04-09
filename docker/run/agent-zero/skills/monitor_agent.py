#!/usr/bin/env python3
"""
Monitor Agent Zero - Supervision en temps réel de l'agent autonome
Affiche l'état des tâches, mémoire, et intégrations Hermes/Notion
"""

import json
import os
from datetime import datetime
from pathlib import Path

class AgentMonitor:
    """Moniteur pour Agent Zero avec intégration Hermes"""
    
    def __init__(self):
        self.scheduler_file = Path("/a0/usr/scheduler/tasks.json")
        self.memory_dir = Path("/a0/memory")
        self.notion_index = Path("/a0/usr/projects/notion_technical_index.json")
        self.hermes_url = "http://llamacpp:8081/v1"
        
    def get_system_time(self):
        """Obtenir l'heure système actuelle"""
        return datetime.now()
    
    def check_scheduler_status(self):
        """Vérifier le statut du scheduler"""
        try:
            if self.scheduler_file.exists():
                with open(self.scheduler_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                tasks = data.get('tasks', [])
                enabled_tasks = [t for t in tasks if t.get('enabled', False)]
                
                return {
                    'status': 'active',
                    'total_tasks': len(tasks),
                    'enabled_tasks': len(enabled_tasks),
                    'tasks': enabled_tasks
                }
            else:
                return {'status': 'no_scheduler', 'tasks': []}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_memory_status(self):
        """Vérifier le statut de la mémoire"""
        try:
            memory_info = {}
            
            # Vérifier les répertoires mémoire
            if self.memory_dir.exists():
                memory_dirs = [d for d in self.memory_dir.iterdir() if d.is_dir()]
                memory_info['memory_directories'] = len(memory_dirs)
                memory_info['directories'] = [d.name for d in memory_dirs]
            else:
                memory_info['memory_directories'] = 0
                memory_info['directories'] = []
            
            # Vérifier les fichiers mémoire dans chaque répertoire
            total_memory_files = 0
            for memory_dir in self.memory_dir.glob("*/"):
                files = list(memory_dir.glob("*"))
                total_memory_files += len(files)
                memory_info[f'{memory_dir.name}_files'] = len(files)
            
            memory_info['total_memory_files'] = total_memory_files
            memory_info['status'] = 'active' if total_memory_files > 0 else 'empty'
            
            return memory_info
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_notion_index_status(self):
        """Vérifier le statut de l'index Notion"""
        try:
            if self.notion_index.exists():
                with open(self.notion_index, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                documents_count = len(index_data)
                
                # Analyser les catégories
                categories = {}
                for doc_id, doc_data in index_data.items():
                    category = doc_data.get('metadata', {}).get('category', 'unknown')
                    categories[category] = categories.get(category, 0) + 1
                
                return {
                    'status': 'active',
                    'documents_count': documents_count,
                    'categories': categories,
                    'last_update': datetime.fromtimestamp(self.notion_index.stat().st_mtime).isoformat()
                }
            else:
                return {'status': 'no_index', 'documents_count': 0}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def check_hermes_status(self):
        """Vérifier le statut de Hermes LLM"""
        try:
            import requests
            
            # Test de connexion
            response = requests.get(f"{self.hermes_url}/models", timeout=5)
            
            if response.status_code == 200:
                models = response.json()
                return {
                    'status': 'active',
                    'models_count': len(models.get('data', [])),
                    'model': models.get('data', [{}])[0].get('id', 'Unknown'),
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    'status': 'error',
                    'http_status': response.status_code,
                    'error': 'HTTP Error'
                }
        except Exception as e:
            return {'status': 'offline', 'error': str(e)}
    
    def get_next_scheduled_tasks(self, hours_ahead=24):
        """Obtenir les prochaines tâches planifiées"""
        try:
            scheduler_status = self.check_scheduler_status()
            if scheduler_status['status'] != 'active':
                return []
            
            current_time = self.get_system_time()
            upcoming_tasks = []
            
            # Pour simplifier, on retourne toutes les tâches actives
            # Dans une version complète, on calculerait les prochaines exécutions
            for task in scheduler_status['tasks']:
                schedule = task.get('schedule', 'Unknown')
                upcoming_tasks.append({
                    'name': task.get('name', 'Unknown'),
                    'schedule': schedule,
                    'description': task.get('description', 'No description'),
                    'agent': task.get('agent', 'Unknown'),
                    'priority': task.get('priority', 'normal')
                })
            
            return upcoming_tasks
        except Exception as e:
            return []
    
    def display_dashboard(self):
        """Afficher le dashboard de monitoring"""
        print("🤖 AGENT ZERO MONITORING DASHBOARD")
        print("=" * 60)
        print(f"🕐 Heure système: {self.get_system_time().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Status Scheduler
        scheduler_status = self.check_scheduler_status()
        print("📋 SCHEDULER STATUS")
        print("-" * 30)
        if scheduler_status['status'] == 'active':
            print(f"✅ Status: Actif")
            print(f"📊 Tâches totales: {scheduler_status['total_tasks']}")
            print(f"🚀 Tâches actives: {scheduler_status['enabled_tasks']}")
        else:
            print(f"❌ Status: {scheduler_status['status']}")
        print()
        
        # Status Mémoire
        memory_status = self.check_memory_status()
        print("🧠 MEMORY STATUS")
        print("-" * 30)
        if memory_status['status'] == 'active':
            print(f"✅ Status: Actif")
            print(f"📁 Répertoires mémoire: {memory_status['memory_directories']}")
            print(f"📄 Fichiers mémoire totaux: {memory_status['total_memory_files']}")
            if memory_status.get('directories'):
                print(f"📂 Répertoires: {', '.join(memory_status['directories'])}")
        else:
            print(f"⚠️  Status: {memory_status['status']}")
        print()
        
        # Status Index Notion
        notion_status = self.check_notion_index_status()
        print("📚 NOTION RAG STATUS")
        print("-" * 30)
        if notion_status['status'] == 'active':
            print(f"✅ Status: Actif")
            print(f"📄 Documents indexés: {notion_status['documents_count']}")
            print("🏷️  Catégories:")
            for category, count in notion_status['categories'].items():
                print(f"   • {category}: {count}")
        else:
            print(f"⚠️  Status: {notion_status['status']}")
        print()
        
        # Status Hermes
        hermes_status = self.check_hermes_status()
        print("🔮 HERMES LLM STATUS")
        print("-" * 30)
        if hermes_status['status'] == 'active':
            print(f"✅ Status: Actif")
            print(f"🤖 Modèles: {hermes_status['models_count']}")
            print(f"📝 Modèle actif: {hermes_status['model']}")
            print(f"⚡ Temps réponse: {hermes_status['response_time_ms']:.0f}ms")
        else:
            print(f"❌ Status: {hermes_status['status']}")
        print()
        
        # Prochaines tâches
        upcoming_tasks = self.get_next_scheduled_tasks()
        print("⏰ UPCOMING TASKS (24h)")
        print("-" * 30)
        if upcoming_tasks:
            for i, task in enumerate(upcoming_tasks[:5], 1):
                priority_emoji = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'normal' else "🟢"
                print(f"{i}. {priority_emoji} {task['name']}")
                print(f"   📅 {task['schedule']}")
                print(f"   🤖 Agent: {task['agent']}")
                print()
        else:
            print("❌ Aucune tâche planifiée")
        print()
        
        # Résumé système
        print("📊 SYSTEM SUMMARY")
        print("-" * 30)
        components_ok = 0
        total_components = 4
        
        if scheduler_status['status'] == 'active':
            components_ok += 1
        if memory_status['status'] != 'error':
            components_ok += 1
        if notion_status['status'] == 'active':
            components_ok += 1
        if hermes_status['status'] == 'active':
            components_ok += 1
        
        health_percent = (components_ok / total_components) * 100
        
        if health_percent == 100:
            print("🟢 SYSTEM HEALTH: EXCELLENT (100%)")
        elif health_percent >= 75:
            print("🟡 SYSTEM HEALTH: GOOD ({}%)".format(int(health_percent)))
        else:
            print("🔴 SYSTEM HEALTH: NEEDS ATTENTION ({}%)".format(int(health_percent)))
        
        print(f"✅ Components OK: {components_ok}/{total_components}")
        print("=" * 60)

def main():
    """Fonction principale"""
    monitor = AgentMonitor()
    
    try:
        monitor.display_dashboard()
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring arrêté")
    except Exception as e:
        print(f"\n❌ Erreur monitoring: {e}")

if __name__ == "__main__":
    main()
