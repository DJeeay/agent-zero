import os
import time
import numpy as np
import faiss
from memory_engine_final import MemoryEngineIVF

# Initialize memory engine
memory = MemoryEngineIVF()

# Add example entries
memory.add([
    "The Eiffel Tower is in Paris",
    "Cats are domestic animals",
    "Quantum mechanics studies particles"
])

# Example repeated entry (tests importance/weighting)
memory.add(["Cats are domestic animals"])

# Perform a search query
query = "Where is the Eiffel Tower?"
results = memory.search(query, k=3)

# Print results
print(f"\nQuery: {query}\nResults:")
for r in results:
    print(r)