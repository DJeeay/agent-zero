#!/usr/bin/env python3
"""
RAG Integration Tool for Agent Zero + Hermes
Integrates FAISS vector store with Hermes LLM for enhanced document retrieval
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

# LangChain imports
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGIntegration:
    """RAG System integrated with Agent Zero and Hermes LLM"""
    
    def __init__(self, 
                 index_path: str = "/a0/usr/projects/rag/faiss_index",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 hermes_url: str = "http://llamacpp:8081/v1"):
        
        self.index_path = Path(index_path)
        self.embedding_model = embedding_model
        self.hermes_url = hermes_url
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cuda' if os.system('nvidia-smi') == 0 else 'cpu'}
        )
        
        # Initialize vector store
        self.vector_store = self._load_or_create_vector_store()
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
        )
        
    def _load_or_create_vector_store(self) -> FAISS:
        """Load existing FAISS index or create new one"""
        if self.index_path.exists():
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            return FAISS.load_local(str(self.index_path), self.embeddings)
        else:
            logger.info("Creating new FAISS index")
            self.index_path.mkdir(parents=True, exist_ok=True)
            # Create empty index with dummy document
            dummy_doc = Document(page_content="Initial document", metadata={"source": "init"})
            return FAISS.from_documents([dummy_doc], self.embeddings)
    
    def index_document(self, 
                      file_path: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Index a document into FAISS vector store
        
        Args:
            file_path: Path to document file
            metadata: Additional metadata for the document
            
        Returns:
            bool: Success status
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Read document content
            content = self._read_document(file_path)
            if not content:
                logger.error(f"Could not read content from {file_path}")
                return False
            
            # Prepare metadata
            doc_metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "file_type": file_path.suffix,
                "indexed_at": str(Path().cwd()),
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(content)
            documents = [
                Document(page_content=chunk, metadata=doc_metadata.copy())
                for chunk in chunks if chunk.strip()
            ]
            
            # Add to vector store
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"Indexed {len(documents)} chunks from {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error indexing document {file_path}: {e}")
            return False
    
    def search_documents(self, 
                        query: str, 
                        k: int = 5,
                        score_threshold: float = 0.7) -> List[Document]:
        """
        Search for relevant documents using semantic similarity
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of relevant documents
        """
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(
                query, k=k
            )
            
            # Filter by score threshold
            filtered_results = [
                doc for doc, score in results 
                if score >= score_threshold
            ]
            
            logger.info(f"Found {len(filtered_results)} relevant documents for query: {query}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def enhance_hermes_context(self, 
                              query: str, 
                              k: int = 3) -> Dict[str, Any]:
        """
        Enhance Hermes context with RAG results
        
        Args:
            query: Original query
            k: Number of documents to retrieve
            
        Returns:
            Enhanced context for Hermes
        """
        # Get relevant documents
        relevant_docs = self.search_documents(query, k=k)
        
        if not relevant_docs:
            return {
                "query": query,
                "context": "No relevant documents found.",
                "sources": []
            }
        
        # Build context string
        context_parts = []
        sources = []
        
        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"Document {i}: {doc.page_content}")
            sources.append({
                "source": doc.metadata.get("source", "Unknown"),
                "filename": doc.metadata.get("filename", "Unknown"),
                "file_type": doc.metadata.get("file_type", "Unknown")
            })
        
        enhanced_context = "\n\n".join(context_parts)
        
        return {
            "query": query,
            "context": enhanced_context,
            "sources": sources,
            "num_documents": len(relevant_docs)
        }
    
    def save_index(self) -> bool:
        """Save the FAISS index to disk"""
        try:
            self.index_path.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(str(self.index_path))
            logger.info(f"FAISS index saved to {self.index_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            return False
    
    def _read_document(self, file_path: Path) -> str:
        """Read content from various document formats"""
        try:
            suffix = file_path.suffix.lower()
            
            if suffix == '.txt':
                return file_path.read_text(encoding='utf-8')
            elif suffix == '.md':
                return file_path.read_text(encoding='utf-8')
            elif suffix == '.json':
                data = json.loads(file_path.read_text(encoding='utf-8'))
                return json.dumps(data, indent=2, ensure_ascii=False)
            elif suffix in ['.py', '.js', '.html', '.css', '.yaml', '.yml']:
                return file_path.read_text(encoding='utf-8')
            else:
                logger.warning(f"Unsupported file type: {suffix}")
                return ""
                
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index"""
        try:
            # This is a simplified version - in practice you'd need FAISS internals
            return {
                "index_path": str(self.index_path),
                "embedding_model": self.embedding_model,
                "index_exists": self.index_path.exists(),
                "hermes_url": self.hermes_url
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}

# Example usage functions for Agent Zero
def index_project_documents(project_path: str) -> bool:
    """Index all documents in a project directory"""
    rag = RAGIntegration()
    project_path = Path(project_path)
    
    if not project_path.exists():
        logger.error(f"Project path not found: {project_path}")
        return False
    
    # Find all supported documents
    supported_extensions = {'.txt', '.md', '.json', '.py', '.js', '.html', '.css', '.yaml', '.yml'}
    documents = []
    
    for ext in supported_extensions:
        documents.extend(project_path.rglob(f"*{ext}"))
    
    # Index each document
    success_count = 0
    for doc_path in documents:
        metadata = {
            "project": project_path.name,
            "relative_path": str(doc_path.relative_to(project_path))
        }
        if rag.index_document(doc_path, metadata):
            success_count += 1
    
    # Save the updated index
    rag.save_index()
    
    logger.info(f"Indexed {success_count}/{len(documents)} documents from {project_path}")
    return success_count > 0

def search_with_rag(query: str, k: int = 5) -> Dict[str, Any]:
    """Search using RAG and return enhanced context"""
    rag = RAGIntegration()
    return rag.enhance_hermes_context(query, k)

if __name__ == "__main__":
    # Example usage
    print("RAG Integration Tool for Agent Zero + Hermes")
    
    # Index documents example
    # index_project_documents("/a0/usr/projects/presparc")
    
    # Search example
    # result = search_with_rag("objectifs d'apprentissage")
    # print(json.dumps(result, indent=2, ensure_ascii=False))
