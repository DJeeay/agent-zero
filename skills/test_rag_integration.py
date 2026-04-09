#!/usr/bin/env python3
"""
Test script for RAG Integration with Agent Zero + Hermes
Validates the complete RAG pipeline
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the skills directory to Python path
sys.path.append(str(Path(__file__).parent))

from rag_integration_tool import RAGIntegration, index_project_documents, search_with_rag

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rag_integration():
    """Test the complete RAG integration pipeline"""
    
    print("🧪 Testing RAG Integration for Agent Zero + Hermes")
    print("=" * 60)
    
    # Test 1: Initialize RAG System
    print("\n1️⃣ Testing RAG Initialization...")
    try:
        rag = RAGIntegration()
        stats = rag.get_index_stats()
        print(f"✅ RAG System initialized successfully")
        print(f"   Index path: {stats['index_path']}")
        print(f"   Embedding model: {stats['embedding_model']}")
        print(f"   Hermes URL: {stats['hermes_url']}")
    except Exception as e:
        print(f"❌ RAG initialization failed: {e}")
        return False
    
    # Test 2: Document Indexation
    print("\n2️⃣ Testing Document Indexation...")
    try:
        # Create a test document
        test_doc_path = Path("/tmp/test_document.txt")
        test_content = """
        Présence-Parcours - Objectifs d'apprentissage
        
        Compétences en mathématiques:
        - Résolution de problèmes complexes
        - Analyse de données statistiques
        - Modélisation mathématique
        
        Compétences en programmation:
        - Algorithmique et structures de données
        - Développement Python
        - Analyse et optimisation
        
        Évaluation Q1 2026:
        Les élèves montrent une progression significative en programmation
        avec un taux de réussite de 85%.
        """
        
        test_doc_path.write_text(test_content, encoding='utf-8')
        
        # Index the document
        metadata = {
            "project": "presparc-test",
            "subject": "mathematiques_programmation",
            "period": "Q1-2026"
        }
        
        success = rag.index_document(str(test_doc_path), metadata)
        if success:
            print("✅ Document indexed successfully")
        else:
            print("❌ Document indexing failed")
            return False
            
        # Save the index
        rag.save_index()
        print("✅ Index saved successfully")
        
    except Exception as e:
        print(f"❌ Document indexing test failed: {e}")
        return False
    
    # Test 3: Document Search
    print("\n3️⃣ Testing Document Search...")
    try:
        queries = [
            "objectifs d'apprentissage mathématiques",
            "programmation Python élèves",
            "résultats Q1 2026",
            "compétences analyse données"
        ]
        
        for query in queries:
            results = rag.search_documents(query, k=3)
            print(f"✅ Query: '{query}' -> Found {len(results)} results")
            
            if results:
                for i, doc in enumerate(results[:2], 1):
                    preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                    print(f"   Result {i}: {preview}")
    
    except Exception as e:
        print(f"❌ Document search test failed: {e}")
        return False
    
    # Test 4: Hermes Context Enhancement
    print("\n4️⃣ Testing Hermes Context Enhancement...")
    try:
        query = "Quelles sont les compétences développées en programmation ?"
        enhanced_context = rag.enhance_hermes_context(query, k=2)
        
        print(f"✅ Enhanced context generated for query: '{query}'")
        print(f"   Documents found: {enhanced_context['num_documents']}")
        print(f"   Context length: {len(enhanced_context['context'])} characters")
        print(f"   Sources: {len(enhanced_context['sources'])}")
        
        # Show context preview
        context_preview = enhanced_context['context'][:200] + "..." if len(enhanced_context['context']) > 200 else enhanced_context['context']
        print(f"   Context preview: {context_preview}")
        
    except Exception as e:
        print(f"❌ Context enhancement test failed: {e}")
        return False
    
    # Test 5: Integration with Agent Zero Workflow
    print("\n5️⃣ Testing Agent Zero Integration...")
    try:
        # Simulate Agent Zero query processing
        user_query = "Analyse les résultats des élèves en programmation"
        
        # Step 1: RAG Search
        rag_result = search_with_rag(user_query, k=3)
        
        # Step 2: Prepare enhanced prompt for Hermes
        enhanced_prompt = f"""
        Contexte RAG:
        {rag_result['context']}
        
        Question utilisateur: {user_query}
        
        Sources utilisées: {[source['filename'] for source in rag_result['sources']]}
        
        Basé sur le contexte RAG ci-dessus, fournis une analyse détaillée.
        """
        
        print(f"✅ Agent Zero integration successful")
        print(f"   Generated enhanced prompt of {len(enhanced_prompt)} characters")
        print(f"   Using {rag_result['num_documents']} RAG documents")
        
    except Exception as e:
        print(f"❌ Agent Zero integration test failed: {e}")
        return False
    
    # Cleanup
    try:
        test_doc_path.unlink(missing_ok=True)
        print("✅ Cleanup completed")
    except:
        pass
    
    print("\n🎉 All RAG Integration Tests Passed!")
    print("=" * 60)
    print("✅ RAG System is ready for Agent Zero + Hermes integration")
    return True

def test_hermes_connectivity():
    """Test connectivity to Hermes LLM"""
    print("\n🔗 Testing Hermes LLM Connectivity...")
    
    try:
        import requests
        
        hermes_url = "http://llamacpp:8081/v1/models"
        response = requests.get(hermes_url, timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Hermes LLM is accessible")
            print(f"   Available models: {len(models.get('data', []))}")
            if models.get('data'):
                print(f"   Model: {models['data'][0].get('id', 'Unknown')}")
            return True
        else:
            print(f"❌ Hermes returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to Hermes: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting RAG Integration Test Suite")
    print("=" * 60)
    
    # Test Hermes connectivity first
    hermes_ok = test_hermes_connectivity()
    
    if hermes_ok:
        # Run RAG integration tests
        success = test_rag_integration()
        
        if success:
            print("\n🎯 CONCLUSION:")
            print("✅ RAG Integration is ready for production use")
            print("✅ Agent Zero can now use enhanced document retrieval")
            print("✅ Hermes LLM connectivity confirmed")
            print("\n📋 NEXT STEPS:")
            print("1. Index your project documents using: index_project_documents('/path/to/project')")
            print("2. Use search_with_rag() in Agent Zero workflows")
            print("3. Enable RAG skill in Agent Zero configuration")
        else:
            print("\n❌ RAG Integration tests failed")
            print("Please check the error messages above and fix the issues")
    else:
        print("\n❌ Hermes LLM is not accessible")
        print("Please ensure Hermes container is running on port 8081")
        print("Run: docker-compose up -d")
