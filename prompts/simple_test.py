#!/usr/bin/env python3
"""
Simple test for Unified Memory System
"""

import tempfile
from unified_memory_tools import UnifiedMemorySystem

def test_memory_system():
    print("Testing Unified Memory System...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_system = UnifiedMemorySystem(temp_dir)
        
        # Test 1: Add entries
        print("1. Testing memory_add...")
        result = memory_system.memory_add("memory", "Project uses Python 3.9 with FastAPI")
        print(f"   Result: {result}")
        
        result = memory_system.memory_add("user", "User prefers concise responses")
        print(f"   Result: {result}")
        
        # Test 2: List entries
        print("2. Testing memory_list...")
        result = memory_system.memory_list("all")
        print(f"   Result: {result}")
        
        # Test 3: Search entries
        print("3. Testing memory_search...")
        result = memory_system.memory_search("python", threshold=0.1)
        print(f"   Result: {result}")
        
        # Test 4: Replace entry
        print("4. Testing memory_replace...")
        result = memory_system.memory_replace("memory", "Python 3.9", "Python 3.10 with FastAPI")
        print(f"   Result: {result}")
        
        # Test 5: Remove entry
        print("5. Testing memory_remove...")
        result = memory_system.memory_remove("user", "concise responses")
        print(f"   Result: {result}")
        
        # Test 6: Legacy compatibility
        print("6. Testing legacy memory_save...")
        result = memory_system.memory_save("Legacy test entry")
        print(f"   Result: {result}")
        
        print("7. Testing legacy memory_load...")
        result = memory_system.memory_load("legacy", threshold=0.1)
        print(f"   Result: {result}")
        
        # Test 8: Security scanning
        print("8. Testing security scanning...")
        result = memory_system.memory_add("memory", "import os; os.system('rm -rf /')")
        print(f"   Malicious content result: {result}")
        
        result = memory_system.memory_add("memory", "Safe content about React")
        print(f"   Safe content result: {result}")
        
        print("\nAll tests completed!")

if __name__ == "__main__":
    test_memory_system()
