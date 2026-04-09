"""
Unified Memory System Implementation
Combines file-based persistent memory with semantic search capabilities
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    content: str
    target: str  # 'memory' or 'user'
    timestamp: str
    id: Optional[str] = None


class UnifiedMemorySystem:
    """Unified memory system combining file-based and semantic search approaches"""
    
    def __init__(self, memory_dir: str = "~/.hermes/memories"):
        self.memory_dir = Path(memory_dir).expanduser()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory file paths
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.user_file = self.memory_dir / "USER.md"
        
        # Character limits
        self.memory_limit = 2200
        self.user_limit = 1375
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        # Session search database
        self.session_db = self.memory_dir.parent / "state.db"
        self._init_session_db()
    
    def _initialize_files(self):
        """Initialize memory files if they don't exist"""
        for file_path in [self.memory_file, self.user_file]:
            if not file_path.exists():
                file_path.write_text("")
    
    def _init_session_db(self):
        """Initialize session search database"""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                content TEXT,
                summary TEXT
            )
        ''')
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                content, summary, timestamp
            )
        ''')
        conn.commit()
        conn.close()
    
    def _read_memory_file(self, target: str) -> str:
        """Read content from memory file"""
        if target == "memory":
            return self.memory_file.read_text(encoding='utf-8')
        elif target == "user":
            return self.user_file.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Invalid target: {target}")
    
    def _write_memory_file(self, target: str, content: str):
        """Write content to memory file"""
        if target == "memory":
            self.memory_file.write_text(content, encoding='utf-8')
        elif target == "user":
            self.user_file.write_text(content, encoding='utf-8')
        else:
            raise ValueError(f"Invalid target: {target}")
    
    def _get_current_usage(self, target: str) -> Tuple[int, int]:
        """Get current character usage and limit"""
        content = self._read_memory_file(target)
        current = len(content)
        limit = self.memory_limit if target == "memory" else self.user_limit
        return current, limit
    
    def _parse_entries(self, content: str) -> List[str]:
        """Parse memory content into entries"""
        if not content.strip():
            return []
        # Split by section sign delimiter
        entries = [entry.strip() for entry in content.split('§') if entry.strip()]
        return entries
    
    def _join_entries(self, entries: List[str]) -> str:
        """Join entries into memory content"""
        return ' §\n'.join(entries)
    
    def _find_matching_entry(self, entries: List[str], old_text: str) -> Optional[int]:
        """Find entry index matching the old_text substring"""
        matches = []
        for i, entry in enumerate(entries):
            if old_text in entry:
                matches.append(i)
        
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            # Multiple matches - need more specific text
            matching_entries = [entries[i] for i in matches]
            raise ValueError(f"Multiple entries match '{old_text}'. Be more specific. Matching entries:\n" + 
                           "\n---\n".join(matching_entries))
    
    def _security_scan(self, content: str) -> bool:
        """Basic security scanning for memory content"""
        # Check for common injection patterns
        injection_patterns = [
            r'(?i)(system|exec|eval|__import__|subprocess)',
            r'(?i)(password|secret|key|token)\s*[:=]\s*["\']',
            r'(?i)(ssh|rsa|private.*key)',
            r'[\u200b-\u200f\u2060\ufeff]',  # Invisible characters
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, content):
                return False
        return True
    
    def memory_add(self, target: str, content: str) -> Dict[str, Union[bool, str]]:
        """Add a new memory entry"""
        if not self._security_scan(content):
            return {"success": False, "error": "Content blocked by security scan"}
        
        current, limit = self._get_current_usage(target)
        if current + len(content) > limit:
            return {
                "success": False,
                "error": f"Memory at {current}/{limit} chars. Adding this entry ({len(content)} chars) would exceed the limit.",
                "usage": f"{current}/{limit}"
            }
        
        # Check for duplicates
        existing_content = self._read_memory_file(target)
        if content in existing_content:
            return {"success": True, "message": "No duplicate added"}
        
        # Add entry
        if existing_content.strip():
            new_content = existing_content.rstrip() + f" §\n{content}"
        else:
            new_content = content
        
        self._write_memory_file(target, new_content)
        
        new_current, _ = self._get_current_usage(target)
        return {
            "success": True,
            "message": "Entry added successfully",
            "usage": f"{new_current}/{limit}"
        }
    
    def memory_replace(self, target: str, old_text: str, content: str) -> Dict[str, Union[bool, str]]:
        """Replace an existing memory entry"""
        if not self._security_scan(content):
            return {"success": False, "error": "Content blocked by security scan"}
        
        existing_content = self._read_memory_file(target)
        entries = self._parse_entries(existing_content)
        
        try:
            entry_index = self._find_matching_entry(entries, old_text)
            if entry_index is None:
                return {"success": False, "error": f"No entry found containing '{old_text}'"}
            
            # Replace entry
            entries[entry_index] = content
            new_content = self._join_entries(entries)
            self._write_memory_file(target, new_content)
            
            return {"success": True, "message": "Entry replaced successfully"}
            
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    def memory_remove(self, target: str, old_text: str) -> Dict[str, Union[bool, str]]:
        """Remove a memory entry"""
        existing_content = self._read_memory_file(target)
        entries = self._parse_entries(existing_content)
        
        try:
            entry_index = self._find_matching_entry(entries, old_text)
            if entry_index is None:
                return {"success": False, "error": f"No entry found containing '{old_text}'"}
            
            # Remove entry
            entries.pop(entry_index)
            new_content = self._join_entries(entries)
            self._write_memory_file(target, new_content)
            
            return {"success": True, "message": "Entry removed successfully"}
            
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    def memory_list(self, target: str = "all") -> Dict[str, Union[bool, List, str]]:
        """List all entries in memory store(s)"""
        result = {}
        
        if target in ["memory", "all"]:
            memory_content = self._read_memory_file("memory")
            memory_entries = self._parse_entries(memory_content)
            current, limit = self._get_current_usage("memory")
            result["memory"] = {
                "entries": memory_entries,
                "usage": f"{current}/{limit}",
                "count": len(memory_entries)
            }
        
        if target in ["user", "all"]:
            user_content = self._read_memory_file("user")
            user_entries = self._parse_entries(user_content)
            current, limit = self._get_current_usage("user")
            result["user"] = {
                "entries": user_entries,
                "usage": f"{current}/{limit}",
                "count": len(user_entries)
            }
        
        return {"success": True, "data": result}
    
    def memory_search(self, query: str, threshold: float = 0.7, 
                     target: str = "all", limit: int = 5) -> Dict[str, Union[bool, List]]:
        """Search memory entries using semantic similarity"""
        # For now, implement simple keyword search
        # In a full implementation, this would use embeddings for semantic search
        results = []
        query_lower = query.lower()
        
        stores = ["memory", "user"] if target == "all" else [target]
        
        for store in stores:
            content = self._read_memory_file(store)
            entries = self._parse_entries(content)
            
            for i, entry in enumerate(entries):
                # Simple similarity calculation (would be semantic in full implementation)
                entry_lower = entry.lower()
                similarity = self._calculate_similarity(query_lower, entry_lower)
                
                if similarity >= threshold:
                    results.append({
                        "target": store,
                        "entry": entry,
                        "similarity": similarity,
                        "index": i
                    })
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:limit]
        
        return {"success": True, "results": results, "query": query}
    
    def _calculate_similarity(self, query: str, text: str) -> float:
        """Simple similarity calculation (placeholder for semantic search)"""
        # This is a basic keyword-based similarity
        # In production, use embeddings from models like sentence-transformers
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    # Legacy compatibility methods
    def memory_load(self, query: str, threshold: float = 0.7, 
                   limit: int = 5, filter: str = "") -> Dict[str, Union[bool, List]]:
        """Legacy method for backward compatibility"""
        # Convert to new search method
        return self.memory_search(query, threshold, "all", limit)
    
    def memory_save(self, text: str) -> Dict[str, Union[bool, str]]:
        """Legacy method for backward compatibility"""
        # Default to memory store
        return self.memory_add("memory", text)
    
    def memory_delete(self, ids: str) -> Dict[str, Union[bool, str]]:
        """Legacy method - not fully compatible with new system"""
        return {"success": False, "error": "memory_delete not supported in unified system. Use memory_remove instead."}
    
    def memory_forget(self, query: str, threshold: float = 0.75, 
                     filter: str = "") -> Dict[str, Union[bool, str]]:
        """Legacy method for removing entries by query"""
        search_result = self.memory_search(query, threshold, "all", 100)
        if not search_result["success"]:
            return search_result
        
        removed_count = 0
        for result in search_result["results"]:
            target = result["target"]
            entry = result["entry"]
            # Use first few words as old_text for removal
            old_text = " ".join(entry.split()[:5])
            remove_result = self.memory_remove(target, old_text)
            if remove_result["success"]:
                removed_count += 1
        
        return {"success": True, "message": f"Removed {removed_count} entries matching query"}


# Example usage and testing
if __name__ == "__main__":
    memory_system = UnifiedMemorySystem()
    
    # Test adding entries
    print("Adding entries...")
    result = memory_system.memory_add("memory", "User runs macOS 14 Sonoma, uses Homebrew")
    print(result)
    
    result = memory_system.memory_add("user", "Prefers concise responses, dislikes verbose explanations")
    print(result)
    
    # List entries
    print("\nListing entries...")
    result = memory_system.memory_list("all")
    print(json.dumps(result, indent=2))
    
    # Search entries
    print("\nSearching entries...")
    result = memory_system.memory_search("macOS homebrew")
    print(json.dumps(result, indent=2))
    
    # Replace entry
    print("\nReplacing entry...")
    result = memory_system.memory_replace("memory", "macOS", "User runs macOS 15 Sequoia, uses Homebrew")
    print(result)
