from memory_engine_final import MemoryEngine

memory = MemoryEngine()

# Add memories
memory.add([
    "The Eiffel Tower is in Paris",
    "Cats are domestic animals",
    "Quantum mechanics studies particles"
])

# Duplicate to boost importance
memory.add(["Cats are domestic animals"])

# Search test
results = memory.search("Where is the Eiffel Tower?", k=3)
for r in results:
    print(r)