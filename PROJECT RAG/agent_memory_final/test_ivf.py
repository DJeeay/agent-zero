from memory_engine_final import MemoryEngine

# Initialize memory engine
memory = MemoryEngine()

# Add some memories
memory.add([
    "The Eiffel Tower is in Paris",
    "Cats are domestic animals",
    "Quantum mechanics studies particles"
])

# Duplicate text to boost importance
memory.add(["Cats are domestic animals"])

# Search example
results = memory.search("Where is the Eiffel Tower?", k=3)

for r in results:
    print(r)