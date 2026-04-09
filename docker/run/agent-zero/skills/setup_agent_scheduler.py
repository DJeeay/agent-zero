#!/usr/bin/env python3
"""
Setup Agent Scheduler - Configuration des tâches régulières pour Agent Zero
Configure les tâches quotidiennes, hebdomadaires et mensuelles avec mémoire Hermes
"""

import json
import os
from datetime import datetime
from pathlib import Path

class AgentSchedulerSetup:
    """Configuration du scheduler pour Agent Zero avec intégration Hermes"""
    
    def __init__(self):
        self.scheduler_file = Path("/a0/usr/scheduler/tasks.json")
        self.memory_dir = Path("/a0/memory/default")
        self.setup_dir = Path("/a0/usr/projects/scheduler_setup")
        
        # Tâches prédéfinies
        self.daily_tasks = [
            {
                "name": "daily_maintenance",
                "description": "Maintenance quotidienne système Agent Zero",
                "schedule": "0 6 * * *",  # 6h tous les jours
                "enabled": True,
                "agent": "system",
                "priority": "normal",
                "commands": [
                    "Nettoyer mémoire temporaire",
                    "Vérifier espace disque disponible",
                    "Sauvegarder mémoires critiques",
                    "Mettre à jour index RAG Notion",
                    "Vérifier intégrité système"
                ],
                "hermes_integration": {
                    "memory_consolidation": True,
                    "context_enrichment": True,
                    "reasoning_boost": True
                }
            },
            {
                "name": "notion_daily_sync",
                "description": "Synchronisation quotidienne Notion Présence-Parcours",
                "schedule": "0 8 * * *",  # 8h tous les jours
                "enabled": True,
                "agent": "notion_agent",
                "priority": "high",
                "commands": [
                    "Récupérer nouvelles données élèves",
                    "Mettre à jour progression automatique",
                    "Générer rapports quotidiens",
                    "Envoyer notifications si anomalies",
                    "Mettre à jour base de connaissances"
                ],
                "hermes_integration": {
                    "memory_consolidation": True,
                    "context_enrichment": True,
                    "reasoning_boost": False
                }
            },
            {
                "name": "hermes_memory_consolidation",
                "description": "Consolidation mémoire Hermes avec apprentissage",
                "schedule": "0 22 * * *",  # 22h tous les jours
                "enabled": True,
                "agent": "hermes_memory",
                "priority": "normal",
                "commands": [
                    "Analyser interactions journée",
                    "Identifier connaissances clés à retenir",
                    "Mettre à jour mémoire longue terme FAISS",
                    "Optimiser embeddings pour performance",
                    "Générer résumé apprentissage journée"
                ],
                "hermes_integration": {
                    "memory_consolidation": True,
                    "context_enrichment": True,
                    "reasoning_boost": True
                }
            }
        ]
        
        self.weekly_tasks = [
            {
                "name": "weekly_backup",
                "description": "Sauvegarde complète hebdomadaire système",
                "schedule": "0 2 * * 0",  # Dimanche 2h du matin
                "enabled": True,
                "agent": "system",
                "priority": "high",
                "commands": [
                    "Backup complet mémoires agents",
                    "Archiver logs semaine complète",
                    "Nettoyer anciennes données temporaires",
                    "Vérifier intégrité backups",
                    "Générer rapport backup hebdomadaire"
                ],
                "hermes_integration": {
                    "memory_consolidation": False,
                    "context_enrichment": False,
                    "reasoning_boost": False
                }
            },
            {
                "name": "performance_analysis",
                "description": "Analyse performance et optimisation hebdomadaire",
                "schedule": "0 18 * * 6",  # Samedi 18h
                "enabled": True,
                "agent": "system",
                "priority": "normal",
                "commands": [
                    "Analyser métriques utilisation semaine",
                    "Identifier goulots d'étranglement performance",
                    "Optimiser configurations mémoire",
                    "Générer rapport performance détaillé",
                    "Planifier optimisations semaine suivante"
                ],
                "hermes_integration": {
                    "memory_consolidation": True,
                    "context_enrichment": True,
                    "reasoning_boost": True
                }
            }
        ]
        
        self.monthly_tasks = [
            {
                "name": "monthly_deep_clean",
                "description": "Nettoyage profond et maintenance mensuelle",
                "schedule": "0 3 1 * *",  # 1er du mois 3h du matin
                "enabled": True,
                "agent": "system",
                "priority": "high",
                "commands": [
                    "Reconstruction complète index FAISS",
                    "Nettoyage mémoire vectorielle optimisée",
                    "Archivage anciennes mémoires (>6 mois)",
                    "Mise à jour système et dépendances",
                    "Validation intégrité complète système"
                ],
                "hermes_integration": {
                    "memory_consolidation": True,
                    "context_enrichment": True,
                    "reasoning_boost": True
                }
            },
            {
                "name": "knowledge_update",
                "description": "Mise à jour connaissances et skills mensuelle",
                "schedule": "0 9 15 * *",  # 15 du mois 9h
                "enabled": True,
                "agent": "knowledge_manager",
                "priority": "normal",
                "commands": [
                    "Réindexer documentation technique Notion",
                    "Intégrer nouveaux projets dans base RAG",
                    "Mettre à jour skills agents",
                    "Valider intégrations Hermes",
                    "Générer rapport connaissances"
                ],
                "hermes_integration": {
                    "memory_consolidation": True,
                    "context_enrichment": True,
                    "reasoning_boost": True
                }
            }
        ]
    
    def load_existing_tasks(self):
        """Charger les tâches existantes"""
        if self.scheduler_file.exists():
            try:
                with open(self.scheduler_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"tasks": []}
    
    def save_tasks(self, tasks_data):
        """Sauvegarder les tâches"""
        # Créer le répertoire si nécessaire
        self.scheduler_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup de l'ancien fichier
        if self.scheduler_file.exists():
            backup_file = self.scheduler_file.with_suffix('.json.backup')
            backup_file.write_text(self.scheduler_file.read_text(encoding='utf-8'), encoding='utf-8')
        
        # Sauvegarder nouvelles tâches
        with open(self.scheduler_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Tâches sauvegardées dans: {self.scheduler_file}")
    
    def setup_all_tasks(self):
        """Configurer toutes les tâches régulières"""
        print("🔧 Configuration Agent Scheduler avec Intégration Hermes")
        print("=" * 60)
        
        # Charger tâches existantes
        existing_data = self.load_existing_tasks()
        existing_tasks = existing_data.get('tasks', [])
        
        # Combiner toutes les nouvelles tâches
        all_new_tasks = self.daily_tasks + self.weekly_tasks + self.monthly_tasks
        
        # Identifier tâches à ajouter/mettre à jour
        updated_tasks = []
        added_count = 0
        updated_count = 0
        
        for new_task in all_new_tasks:
            # Chercher si la tâche existe déjà
            existing_task = next((t for t in existing_tasks if t.get('name') == new_task['name']), None)
            
            if existing_task:
                # Mettre à jour la tâche existante
                updated_task = {**existing_task, **new_task}
                updated_tasks.append(updated_task)
                updated_count += 1
                print(f"🔄 Mise à jour: {new_task['name']}")
            else:
                # Ajouter nouvelle tâche
                updated_tasks.append(new_task)
                added_count += 1
                print(f"✅ Nouveau: {new_task['name']}")
        
        # Ajouter les tâches existantes qui n'ont pas été mises à jour
        for existing_task in existing_tasks:
            if not any(t.get('name') == existing_task.get('name') for t in all_new_tasks):
                updated_tasks.append(existing_task)
        
        # Sauvegarder
        tasks_data = {"tasks": updated_tasks}
        self.save_tasks(tasks_data)
        
        # Afficher les statistiques
        self.print_setup_summary(added_count, updated_count, len(updated_tasks))
        
        # Créer fichier de configuration mémoire
        self.setup_memory_config()
        
        return {
            'success': True,
            'added': added_count,
            'updated': updated_count,
            'total': len(updated_tasks)
        }
    
    def setup_memory_config(self):
        """Configurer la mémoire pour les tâches"""
        memory_config = {
            "agent_memory_types": {
                "episodic": "Souvenirs interactions et succès",
                "semantic": "Connaissances générales et concepts", 
                "procedural": "Comment faire les tâches",
                "working": "Informations temporaires travail",
                "long_term": "Mémoire persistante FAISS"
            },
            "hermes_integration": {
                "context_enrichment": True,
                "reasoning_boost": True,
                "cross_agent_sharing": True,
                "continuous_learning": True
            },
            "memory_operations": {
                "auto_consolidation": "22h quotidiennement",
                "backup_schedule": "2h le dimanche",
                "cleanup_old_memories": "1er du mois",
                "optimization_schedule": "3h le dimanche"
            }
        }
        
        # Créer répertoire de configuration
        self.setup_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder configuration mémoire
        memory_config_file = self.setup_dir / "memory_config.json"
        with open(memory_config_file, 'w', encoding='utf-8') as f:
            json.dump(memory_config, f, indent=2, ensure_ascii=False)
        
        print(f"🧠 Configuration mémoire sauvegardée: {memory_config_file}")
    
    def print_setup_summary(self, added, updated, total):
        """Afficher le résumé de la configuration"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ CONFIGURATION SCHEDULER")
        print("=" * 60)
        
        print(f"\n📈 Tâches configurées:")
        print(f"   Nouvelles tâches: {added}")
        print(f"   Tâches mises à jour: {updated}")
        print(f"   Total tâches actives: {total}")
        
        print(f"\n⏰ Planification:")
        print(f"   Tâches quotidiennes: {len(self.daily_tasks)}")
        print(f"   Tâches hebdomadaires: {len(self.weekly_tasks)}")
        print(f"   Tâches mensuelles: {len(self.monthly_tasks)}")
        
        print(f"\n🤖 Intégration Hermes:")
        print(f"   Consolidation mémoire: ✅ Activée")
        print(f"   Enrichissement contexte: ✅ Activé")
        print(f"   Raisonnement amélioré: ✅ Activé")
        
        print(f"\n📁 Fichiers créés:")
        print(f"   Scheduler: {self.scheduler_file}")
        print(f"   Memory: {self.setup_dir}/memory_config.json")
        
        print("\n" + "=" * 60)
        print("🎉 CONFIGURATION TERMINÉE - AGENT ZERO PRÊT !")
        print("=" * 60)
    
    def list_active_tasks(self):
        """Lister les tâches actives"""
        tasks_data = self.load_existing_tasks()
        tasks = tasks_data.get('tasks', [])
        
        print("📋 TÂCHES ACTIVES AGENT ZERO")
        print("=" * 50)
        
        if not tasks:
            print("❌ Aucune tâche configurée")
            return
        
        for task in tasks:
            if task.get('enabled', False):
                status = "✅" if task.get('enabled', False) else "❌"
                print(f"{status} {task.get('name', 'Unknown')}")
                print(f"   📝 {task.get('description', 'No description')}")
                print(f"   ⏰ Schedule: {task.get('schedule', 'No schedule')}")
                print(f"   🤖 Agent: {task.get('agent', 'No agent')}")
                print(f"   🎯 Priority: {task.get('priority', 'normal')}")
                print()

def main():
    """Fonction principale"""
    scheduler = AgentSchedulerSetup()
    
    print("🚀 AGENT ZERO SCHEDULER SETUP")
    print("Configuration tâches régulières avec intégration Hermes")
    print("=" * 60)
    
    # Configuration
    result = scheduler.setup_all_tasks()
    
    if result['success']:
        print(f"\n✅ SUCCÈS: {result['added']} nouvelles tâches, {result['updated']} mises à jour")
        print(f"\n🔍 Pour voir les tâches actives:")
        print("   python3 /a0/skills/setup_agent_scheduler.py list")
        print(f"\n⚡ Les tâches commenceront automatiquement selon leur schedule")
    else:
        print("\n❌ ÉCHEC de la configuration")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        scheduler = AgentSchedulerSetup()
        scheduler.list_active_tasks()
    else:
        main()
