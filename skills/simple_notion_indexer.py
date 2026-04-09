#!/usr/bin/env python3
"""
Indexation simplifiée Notion Technique - Version compatible Agent Zero
Indexe les documents techniques Notion sans dépendances externes
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import re

class SimpleNotionIndexer:
    """Indexation simplifiée pour documents techniques Notion"""
    
    def __init__(self):
        self.base_path = Path("/a0/usr/projects")
        self.index_file = Path("/a0/usr/projects/notion_technical_index.json")
        self.notion_projects = [
            "PROJECT NOTION  PRES PARC",
            "presparc-notion",
            "presparc-notion-skill-v1.0", 
            "presparc-notion-skill-v1.1"
        ]
        
        # Extensions techniques
        self.technical_extensions = {
            '.md', '.txt', '.py', '.js', '.html', '.css', '.yaml', '.yml',
            '.json', '.sql', '.sh', '.bat', '.ps1', '.cfg', '.ini', '.toml'
        }
        
        # Mots-clés techniques
        self.technical_keywords = {
            'notion_api': ['notion', 'api', 'integration', 'database', 'endpoint'],
            'scripting': ['script', 'python', 'automation', 'batch', 'function'],
            'configuration': ['config', 'setup', 'settings', 'env', 'token'],
            'documentation': ['readme', 'doc', 'guide', 'tutorial', 'example'],
            'debugging': ['error', 'fix', 'debug', 'troubleshoot', 'issue'],
            'deployment': ['deploy', 'docker', 'server', 'production', 'run']
        }
    
    def scan_notion_projects(self):
        """Scanne tous les projets Notion"""
        technical_files = []
        
        for project_name in self.notion_projects:
            project_path = self.base_path / project_name
            if not project_path.exists():
                print(f"⚠️  Project not found: {project_path}")
                continue
            
            print(f"📁 Scanning: {project_name}")
            
            for ext in self.technical_extensions:
                files = list(project_path.rglob(f"*{ext}"))
                for file_path in files:
                    technical_files.append({
                        'path': str(file_path),
                        'project': project_name,
                        'relative_path': str(file_path.relative_to(project_path)),
                        'filename': file_path.name,
                        'extension': file_path.suffix
                    })
        
        print(f"📊 Found {len(technical_files)} technical files")
        return technical_files
    
    def classify_document(self, file_path, content):
        """Classification simple du document"""
        content_lower = content.lower()
        file_name_lower = file_path.lower()
        
        scores = {}
        for category, keywords in self.technical_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in content_lower:
                    score += content_lower.count(keyword)
                if keyword in file_name_lower:
                    score += 2
            scores[category] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'general_technical'
    
    def extract_notion_metadata(self, file_path, content):
        """Extraction métadonnées Notion"""
        metadata = {
            'file_type': Path(file_path).suffix,
            'file_size': len(content),
            'indexed_at': datetime.now().isoformat(),
            'line_count': content.count('\n') + 1
        }
        
        # URLs Notion
        notion_urls = re.findall(r'https://www\.notion\.so/[^\s\)]+', content)
        if notion_urls:
            metadata['notion_urls'] = notion_urls
        
        # IDs Notion
        notion_ids = re.findall(r'[a-f0-9]{32}', content.lower())
        if notion_ids:
            metadata['notion_database_ids'] = list(set(notion_ids))
        
        # Propriétés Notion
        notion_props = re.findall(r'"([^"]*)":\s*{[^}]*"type":\s*"[^"]*"', content)
        if notion_props:
            metadata['notion_properties'] = notion_props
        
        return metadata
    
    def create_content_hash(self, content):
        """Crée un hash du contenu pour déduplication"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def index_all_notion_technical(self):
        """Indexation complète"""
        print("🚀 Starting Simple Notion Technical Indexing")
        print("=" * 60)
        
        # Charger l'index existant
        existing_index = self.load_index()
        
        # Scanner les fichiers
        technical_files = self.scan_notion_projects()
        
        if not technical_files:
            print("❌ No technical files found")
            return {'success': False, 'message': 'No files found'}
        
        # Statistiques
        stats = {
            'total_files': len(technical_files),
            'new_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
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
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if len(content.strip()) < 50:
                    print(f"⏭️  Skipping short file: {relative_path}")
                    stats['skipped_files'] += 1
                    continue
                
                # Créer hash
                content_hash = self.create_content_hash(content)
                
                # Vérifier si déjà indexé
                doc_id = f"{project}:{relative_path}"
                if doc_id in existing_index:
                    if existing_index[doc_id].get('content_hash') == content_hash:
                        print(f"⏭️  Unchanged: {relative_path}")
                        stats['skipped_files'] += 1
                        continue
                    else:
                        stats['updated_files'] += 1
                        print(f"🔄 Updated: {relative_path}")
                else:
                    stats['new_files'] += 1
                    print(f"✅ New: {relative_path}")
                
                # Classification
                category = self.classify_document(file_path, content)
                
                # Métadonnées
                metadata = self.extract_notion_metadata(file_path, content)
                metadata.update({
                    'project': project,
                    'relative_path': relative_path,
                    'category': category,
                    'technical_domain': 'notion_integration',
                    'content_hash': content_hash
                })
                
                # Stocker dans l'index
                existing_index[doc_id] = {
                    'content': content[:2000],  # Preview limité
                    'metadata': metadata,
                    'full_path': file_path
                }
                
                # Stats
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                stats['projects'][project] = stats['projects'].get(project, 0) + 1
                stats['file_types'][Path(file_path).suffix] = stats['file_types'].get(Path(file_path).suffix, 0) + 1
                
            except Exception as e:
                print(f"❌ Error indexing {file_path}: {e}")
                stats['skipped_files'] += 1
        
        # Sauvegarder l'index
        self.save_index(existing_index)
        
        # Afficher les stats
        self.print_stats(stats)
        
        return {
            'success': True,
            'stats': stats,
            'message': f"Indexed {stats['new_files']} new, {stats['updated_files']} updated files"
        }
    
    def load_index(self):
        """Charger l'index existant"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_index(self, index_data):
        """Sauvegarder l'index"""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Index saved to: {self.index_file}")
    
    def print_stats(self, stats):
        """Afficher les statistiques"""
        print("\n" + "="*60)
        print("📊 NOTION TECHNICAL INDEXING STATISTICS")
        print("="*60)
        
        print(f"\n📁 Files Processed:")
        print(f"   Total found: {stats['total_files']}")
        print(f"   New files: {stats['new_files']}")
        print(f"   Updated files: {stats['updated_files']}")
        print(f"   Skipped files: {stats['skipped_files']}")
        
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
    
    def search_notion_technical(self, query, limit=10):
        """Recherche simple dans l'index"""
        index = self.load_index()
        query_lower = query.lower()
        
        results = []
        for doc_id, doc_data in index.items():
            content = doc_data['content'].lower()
            metadata = doc_data['metadata']
            
            # Score simple basé sur occurrences
            score = 0
            if query_lower in content:
                score += content.count(query_lower) * 2
            
            # Bonus si query dans métadonnées
            for key, value in metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 3
            
            if score > 0:
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'content_preview': doc_data['content'][:300],
                    'metadata': metadata
                })
        
        # Trier par score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]

def main():
    """Fonction principale"""
    indexer = SimpleNotionIndexer()
    
    print("🔧 SIMPLE NOTION TECHNICAL INDEXER")
    print("Indexation sans dépendances externes")
    print("=" * 60)
    
    # Indexation
    result = indexer.index_all_notion_technical()
    
    if result['success']:
        print(f"\n🎉 SUCCESS: {result['message']}")
        print(f"\n💡 Index saved to: {indexer.index_file}")
        print("\n🔍 You can now search using:")
        print("   python3 /a0/skills/simple_notion_indexer.py search 'your query'")
    else:
        print(f"\n❌ FAILED: {result['message']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        if len(sys.argv) > 2:
            indexer = SimpleNotionIndexer()
            query = " ".join(sys.argv[2:])
            results = indexer.search_notion_technical(query)
            
            print(f"\n🔍 Search Results for: '{query}'")
            print("=" * 50)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['metadata']['relative_path']} (Score: {result['score']})")
                print(f"   Category: {result['metadata'].get('category', 'Unknown')}")
                print(f"   Preview: {result['content_preview'][:200]}...")
        else:
            print("Usage: python3 simple_notion_indexer.py search 'your query'")
    else:
        main()
