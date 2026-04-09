#!/usr/bin/env python3
"""
Comprehensive test suite for the Unified Memory System
"""

import json
import os
import tempfile
import shutil
from unified_memory_tools import UnifiedMemorySystem

def test_basic_operations():
    """Test basic memory operations"""
    print("Testing Basic Operations...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_system = UnifiedMemorySystem(temp_dir)
        
        # Test memory_add
        result = memory_system.memory_add("memory", "Test project uses Python 3.9 with FastAPI")
        assert result["success"], f"memory_add failed: {result}"
        print("memory_add works")
        
        result = memory_system.memory_add("user", "User prefers detailed explanations")
        assert result["success"], f"memory_add to user failed: {result}"
        print("memory_add to user store works")
        
        # Test memory_list
        result = memory_system.memory_list("all")
        assert result["success"], f"memory_list failed: {result}"
        assert len(result["data"]["memory"]["entries"]) == 1
        assert len(result["data"]["user"]["entries"]) == 1
        print("memory_list works")
        
        # Test memory_replace
        result = memory_system.memory_replace("memory", "Python 3.9", "Python 3.10 with FastAPI and SQLAlchemy")
        assert result["success"], f"memory_replace failed: {result}"
        print("memory_replace works")
        
        # Test memory_remove
        result = memory_system.memory_remove("user", "detailed explanations")
        assert result["success"], f"memory_remove failed: {result}"
        print("memory_remove works")
        
        print("Basic operations test passed!\n")

def test_search_functionality():
    """Test semantic search functionality"""
    print("🔍 Testing Search Functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_system = UnifiedMemorySystem(temp_dir)
        
        # Add test entries
        memory_system.memory_add("memory", "Project uses PostgreSQL database with connection pooling")
        memory_system.memory_add("memory", "Frontend built with React and TypeScript")
        memory_system.memory_add("user", "User likes vim keybindings and dark themes")
        
        # Test memory_search
        result = memory_system.memory_search("database", threshold=0.1)
        assert result["success"], f"memory_search failed: {result}"
        assert len(result["results"]) > 0, "Search should find database entry"
        print("✅ memory_search finds relevant entries")
        
        # Test with higher threshold
        result = memory_system.memory_search("database", threshold=0.9)
        assert result["success"], f"memory_search with high threshold failed: {result}"
        print("✅ memory_search with high threshold works")
        
        print("✅ Search functionality test passed!\n")

def test_capacity_management():
    """Test capacity limits and management"""
    print("📏 Testing Capacity Management...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create system with very small limits for testing
        memory_system = UnifiedMemorySystem(temp_dir)
        memory_system.memory_limit = 100  # Very small for testing
        memory_system.user_limit = 50
        
        # Fill up memory
        long_entry = "x" * 50
        result = memory_system.memory_add("memory", long_entry)
        assert result["success"], "First entry should succeed"
        
        result = memory_system.memory_add("memory", long_entry)
        assert result["success"], "Second entry should succeed"
        
        # This should fail due to capacity limit
        result = memory_system.memory_add("memory", long_entry)
        assert not result["success"], "Third entry should fail due to capacity"
        assert "exceed the limit" in result["error"]
        print("✅ Capacity limits enforced")
        
        # Test consolidation via replace
        result = memory_system.memory_replace("memory", long_entry, "x" * 80)
        assert result["success"], "Replace should work even when full"
        print("✅ Memory consolidation works")
        
        print("✅ Capacity management test passed!\n")

def test_security_scanning():
    """Test security scanning functionality"""
    print("🔒 Testing Security Scanning...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_system = UnifiedMemorySystem(temp_dir)
        
        # Test malicious content blocking
        malicious_content = "import os; os.system('rm -rf /')"
        result = memory_system.memory_add("memory", malicious_content)
        assert not result["success"], "Malicious content should be blocked"
        assert "security scan" in result["error"]
        print("✅ Malicious content blocked")
        
        # Test invisible characters
        invisible_content = "Normal text\u200bwith invisible chars"
        result = memory_system.memory_add("memory", invisible_content)
        assert not result["success"], "Invisible characters should be blocked"
        print("✅ Invisible characters blocked")
        
        # Test safe content
        safe_content = "Project uses React and Node.js"
        result = memory_system.memory_add("memory", safe_content)
        assert result["success"], "Safe content should be allowed"
        print("✅ Safe content allowed")
        
        print("✅ Security scanning test passed!\n")

def test_legacy_compatibility():
    """Test backward compatibility with legacy operations"""
    print("🔄 Testing Legacy Compatibility...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_system = UnifiedMemorySystem(temp_dir)
        
        # Test memory_save (legacy)
        result = memory_system.memory_save("Legacy test entry")
        assert result["success"], f"memory_save failed: {result}"
        print("✅ memory_save (legacy) works")
        
        # Test memory_load (legacy)
        result = memory_system.memory_load("test", threshold=0.1)
        assert result["success"], f"memory_load failed: {result}"
        print("✅ memory_load (legacy) works")
        
        # Test memory_forget (legacy)
        result = memory_system.memory_forget("legacy", threshold=0.1)
        assert result["success"], f"memory_forget failed: {result}"
        print("✅ memory_forget (legacy) works")
        
        # Test memory_delete (should show limited compatibility)
        result = memory_system.memory_delete("test-id")
        assert not result["success"], "memory_delete should show limited compatibility"
        assert "not supported" in result["error"]
        print("✅ memory_delete properly shows limited compatibility")
        
        print("✅ Legacy compatibility test passed!\n")

def test_duplicate_prevention():
    """Test duplicate entry prevention"""
    print("🚫 Testing Duplicate Prevention...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_system = UnifiedMemorySystem(temp_dir)
        
        # Add an entry
        content = "Unique test entry for duplicate testing"
        result = memory_system.memory_add("memory", content)
        assert result["success"], "First addition should succeed"
        
        # Try to add the same entry
        result = memory_system.memory_add("memory", content)
        assert result["success"], "Duplicate addition should succeed but not add"
        assert "no duplicate added" in result["message"]
        print("✅ Duplicate entries prevented")
        
        # Verify only one entry exists
        result = memory_system.memory_list("memory")
        assert len(result["data"]["memory"]["entries"]) == 1
        print("✅ Only one entry stored")
        
        print("✅ Duplicate prevention test passed!\n")

def run_all_tests():
    """Run all test suites"""
    print("Starting Unified Memory System Test Suite\n")
    print("=" * 50)
    
    try:
        test_basic_operations()
        test_search_functionality()
        test_capacity_management()
        test_security_scanning()
        test_legacy_compatibility()
        test_duplicate_prevention()
        
        print("=" * 50)
        print("All tests passed! The Unified Memory System is working correctly.")
        print("\nTest Summary:")
        print("Basic Operations (add, replace, remove, list)")
        print("Search Functionality (semantic search)")
        print("Capacity Management (limits, consolidation)")
        print("Security Scanning (injection prevention)")
        print("Legacy Compatibility (backward compatibility)")
        print("Duplicate Prevention (no duplicates)")
        
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
