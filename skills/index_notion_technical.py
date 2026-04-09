#!/usr/bin/env python3
"""
Indexation complète de la technicité Notion pour Agent Zero + Hermes RAG
Indexe tous les documents techniques, scripts, et configurations Notion
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Add skills directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from rag_integration_tool import RAGIntegration
except ImportError:
    print("❌ RAG Integration tool not available. Please ensure dependencies are installed.")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NotionTechnicalIndexer:
    """Spécialisé dans l'indexation de la technicité Notion"""
    
    def __init__(self):
        self.rag = RAGIntegration()
        self.base_path = Path("/a0/usr/projects")
        self.notion_projects = [
            "PROJECT NOTION  PRES PARC",
            "presparc-notion",
            "presparc-notion-skill-v1.0", 
            "presparc-notion-skill-v1.1"
        ]
        
        # Types de documents techniques à indexer
        self.technical_extensions = {
            '.md', '.txt', '.py', '.js', '.html', '.css', '.yaml', '.yml',
            '.json', '.sql', '.sh', '.bat', '.ps1', '.cfg', '.ini', '.toml'
        }
        
        # Mots-clés techniques pour classification
        self.technical_keywords = {
            'notion_api': ['notion', 'api', 'integration', 'database'],
            'scripting': ['script', 'python', 'automation', 'batch'],
            'configuration': ['config', 'setup', 'settings', 'env'],
            'documentation': ['readme', 'doc', 'guide', 'tutorial'],
            'debugging': ['error', 'fix', 'debug', 'troubleshoot'],
            'deployment': ['deploy', 'docker', 'server', 'production']
        }
    
    def scan_notion_projects(self) -> list:
        """Scanne tous les projets Notion et retourne les fichiers techniques"""
        technical_files = []
        
        for project_name in self.notion_projects:
            project_path = self.base_path / project_name
            if not project_path.exists():
                logger.warning(f"Project not found: {project_path}")
                continue
            
            logger.info(f"Scanning project: {project_name}")
            
            # Scan récursif pour les fichiers techniques
            for ext in self.technical_extensions:
                files = list(project_path.rglob(f"*{ext}"))
                for file_path in files:
                    technical_files.append({
                        'path': file_path,
                        'project': project_name,
                        'relative_path': str(file_path.relative_to(project_path))
                    })
        
        logger.info(f"Found {len(technical_files)} technical files")
        return technical_files
    
    def classify_document(self, file_path: Path, content: str) -> str:
        """Classifie le document selon sa thématique technique"""
        content_lower = content.lower()
        file_name_lower = file_path.name.lower()
        
        scores = {}
        for category, keywords in self.technical_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += content_lower.count(keyword)
                if keyword in file_name_lower:
                    score += 2  # Poids plus élevé pour le nom de fichier
            scores[category] = score
        
        # Retourner la catégorie avec le score le plus élevé
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'general_technical'
    
    def extract_notion_metadata(self, file_path: Path, content: str) -> dict:
        """Extrait les métadonnées spécifiques Notion"""
        metadata = {
            'file_type': file_path.suffix,
            'file_size': len(content),
            'indexed_at': datetime.now().isoformat(),
            'line_count': content.count('\n') + 1
        }
        
        # Extraire les URLs Notion si présentes
        import re
        notion_urls = re.findall(r'https://www\.notion\.so/[^\s\)]+', content)
        if notion_urls:
            metadata['notion_urls'] = notion_urls
        
        # Extraire les IDs de base Notion
        notion_ids = re.findall(r'[a-f0-9]{32}', content.lower())
        if notion_ids:
            metadata['notion_database_ids'] = list(set(notion_ids))
        
        # Extraire les noms de propriétés Notion
        notion_props = re.findall(r'"([^"]*)":\s*{[^}]*"type":\s*"[^"]*"', content)
        if notion_props:
            metadata['notion_properties'] = notion_props
        
        return metadata
    
    def index_all_notion_technical(self) -> dict:
        """Indexe toute la technicité Notion"""
        logger.info("🚀 Starting complete Notion technical indexing")
        
        # Scanner les fichiers
        technical_files = self.scan_notion_projects()
        
        if not technical_files:
            logger.error("No technical files found to index")
            return {'success': False, 'message': 'No files found'}
        
        # Statistiques d'indexation
        stats = {
            'total_files': len(technical_files),
            'indexed_files': 0,
            'failed_files': 0,
            'categories': {},
            'projects': {},
            'file_types': {}
        }
        
        # Indexer chaque fichier
        for file_info in technical_files:
            file_path = file_info['path']
            project = file_info['project']
            relative_path = file_info['relative_path']
            
            try:
                # Lire le contenu
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                if len(content.strip()) < 50:  # Ignorer les fichiers trop courts
                    logger.debug(f"Skipping short file: {file_path}")
                    continue
                
                # Classification
                category = self.classify_document(file_path, content)
                
                # Métadonnées enrichies
                metadata = self.extract_notion_metadata(file_path, content)
                metadata.update({
                    'project': project,
                    'relative_path': relative_path,
                    'category': category,
                    'technical_domain': 'notion_integration'
                })
                
                # Indexer dans RAG
                success = self.rag.index_document(str(file_path), metadata)
                
                if success:
                    stats['indexed_files'] += 1
                    stats['categories'][category] = stats['categories'].get(category, 0) + 1
                    stats['projects'][project] = stats['projects'].get(project, 0) + 1
                    stats['file_types'][file_path.suffix] = stats['file_types'].get(file_path.suffix, 0) + 1
                    
                    logger.info(f"✅ Indexed: {relative_path} [{category}]")
                else:
                    stats['failed_files'] += 1
                    logger.error(f"❌ Failed to index: {file_path}")
                
            except Exception as e:
                stats['failed_files'] += 1
                logger.error(f"❌ Error indexing {file_path}: {e}")
        
        # Sauvegarder l'index
        self.rag.save_index()
        
        # Afficher les statistiques
        self._print_indexing_stats(stats)
        
        return {
            'success': True,
            'stats': stats,
            'message': f"Indexed {stats['indexed_files']}/{stats['total_files']} technical files"
        }
    
    def _print_indexing_stats(self, stats: dict):
        """Affiche les statistiques d'indexation"""
        print("\n" + "="*60)
        print("📊 NOTION TECHNICAL INDEXING STATISTICS")
        print("="*60)
        
        print(f"\n📁 Files Processed:")
        print(f"   Total found: {stats['total_files']}")
        print(f"   Successfully indexed: {stats['indexed_files']}")
        print(f"   Failed: {stats['failed_files']}")
        print(f"   Success rate: {(stats['indexed_files']/stats['total_files']*100):.1f}%")
        
        if stats['categories']:
            print(f"\n🏷️  By Category:")
            for category, count in sorted(stats['categories'].items()):
                print(f"   {category}: {count}")
        
        if stats['projects']:
            print(f"\n📂 By Project:")
            for project, count in sorted(stats['projects'].items()):
                print(f"   {project}: {count}")
        
        if stats['file_types']:
            print(f"\n📄 By File Type:")
            for ext, count in sorted(stats['file_types'].items()):
                print(f"   {ext}: {count}")
        
        print("\n" + "="*60)
    
    def search_notion_technical(self, query: str, k: int = 5) -> dict:
        """Recherche spécifique dans la technicité Notion"""
        # Recherche RAG standard
        results = self.rag.search_documents(query, k=k)
        
        # Filtrer pour ne garder que les documents techniques Notion
        notion_results = []
        for doc in results:
            metadata = doc.metadata
            if metadata.get('technical_domain') == 'notion_integration':
                notion_results.append(doc)
        
        logger.info(f"Found {len(notion_results)} Notion technical results for: {query}")
        
        return {
            'query': query,
            'results': notion_results,
            'count': len(notion_results)
        }

def main():
    """Fonction principale pour l'indexation"""
    indexer = NotionTechnicalIndexer()
    
    print("🔧 NOTION TECHNICAL INDEXER")
    print("Indexation complète de la technicité Notion pour Agent Zero + Hermes")
    print("="*60)
    
    # Lancer l'indexation
    result = indexer.index_all_notion_technical()
    
    if result['success']:
        print(f"\n🎉 SUCCESS: {result['message']}")
        print("\n💡 You can now search Notion technical content using:")
        print("   - 'Recherche dans la documentation technique Notion'")
        print("   - 'Trouve les scripts d\\'automatisation Notion'")
        print("   - 'Comment configurer l\\'API Notion ?'")
    else:
        print(f"\n❌ FAILED: {result['message']}")

if __name__ == "__main__":
    main()
