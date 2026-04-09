import os
import json
import time
import faiss
import numpy as np
from typing import List, Dict
from litellm import embedding

# -------------------------
# Configuration (all essential options)
# -------------------------
MODEL = "ollama/nomic-embed-text"
DIM = 768

INDEX_FILE = "memory_index.faiss"
META_FILE = "memory_meta.json"

DECAY_LAMBDA = 0.0001       # memory decay
IMPORTANCE_BOOST = 1.5      # repeated memory importance
MAX_MEMORY = 50000           # max memory entries
BATCH_SAVE = True            # store embeddings in metadata

IVF_NPROBE = 10              # IVF search probes
HNSW_EFSEARCH = 50           # HNSW efSearch

# -------------------------
# Memory Engine
# -------------------------
class MemoryEngine:
    def __init__(self):
        self.metadata: List[Dict] = self._load_metadata()
        self.index = None
        self._load_index()

    # -------------------------
    # Persistence
    # -------------------------
    def _load_metadata(self):
        if os.path.exists(META_FILE):
            with open(META_FILE, "r") as f:
                return json.load(f)
        return []

    def _save(self):
        if self.index:
            faiss.write_index(self.index, INDEX_FILE)
        with open(META_FILE, "w") as f:
            json.dump(self.metadata, f)

    # -------------------------
    # Embedding helper
    # -------------------------
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), DIM), dtype="float32")
        to_embed, to_embed_idx = [], []

        if BATCH_SAVE:
            for i, text in enumerate(texts):
                for m in self.metadata:
                    if m["text"] == text and "vector" in m:
                        vectors[i] = np.array(m["vector"], dtype="float32")
                        break
                else:
                    to_embed.append(text)
                    to_embed_idx.append(i)
        else:
            to_embed = texts
            to_embed_idx = list(range(len(texts)))

        if to_embed:
            resp = embedding(model=MODEL, input=to_embed)
            new_vectors = np.array([d["embedding"] for d in resp["data"]], dtype="float32")
            faiss.normalize_L2(new_vectors)
            for i, vec in zip(to_embed_idx, new_vectors):
                vectors[i] = vec

        return vectors

    # -------------------------
    # Auto-index selection
    # -------------------------
    def _select_index_type(self, n_vectors: int):
        if n_vectors < 1000:
            return "flat"
        elif n_vectors < 50000:
            return "ivf"
        else:
            return "hnsw"

    # -------------------------
    # Create FAISS index
    # -------------------------
    def _create_index(self, n_vectors: int):
        index_type = self._select_index_type(n_vectors)
        if index_type == "flat":
            return faiss.IndexFlatIP(DIM)
        elif index_type == "ivf":
            nlist = max(1, int(np.sqrt(n_vectors)))
            quantizer = faiss.IndexFlatIP(DIM)
            index = faiss.IndexIVFFlat(quantizer, DIM, nlist, faiss.METRIC_INNER_PRODUCT)
            index.nprobe = min(IVF_NPROBE, nlist)
            return index
        elif index_type == "hnsw":
            index = faiss.IndexHNSWFlat(DIM, 32)
            index.hnsw.efSearch = HNSW_EFSEARCH
            return index
        else:
            raise ValueError("Unknown index type")

    def _load_index(self):
        if os.path.exists(INDEX_FILE):
            self.index = faiss.read_index(INDEX_FILE)

    # -------------------------
    # Add memory entries
    # -------------------------
    def add(self, texts: List[str], extra_meta: List[Dict] = None):
        vectors = self._embed_batch(texts)
        total_vectors = len(self.metadata) + len(vectors)

        # Evict oldest memories if exceeding max
        if MAX_MEMORY > 0 and total_vectors > MAX_MEMORY:
            overflow = total_vectors - MAX_MEMORY
            self.metadata = self.metadata[overflow:]
            if self.index:
                self.index = self._create_index(len(self.metadata))
                if len(self.metadata) > 0:
                    all_vectors = np.array([m["vector"] for m in self.metadata], dtype="float32")
                    self.index.add(all_vectors)
            total_vectors = len(self.metadata) + len(vectors)

        # Create index if missing
        if self.index is None:
            self.index = self._create_index(total_vectors)

        # Train IVF if needed
        if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
            self.index.train(vectors)

        now = time.time()
        for i, text in enumerate(texts):
            existing = [m for m in self.metadata if m["text"] == text]
            importance = IMPORTANCE_BOOST if existing else 1.0
            meta = {
                "text": text,
                "timestamp": now,
                "importance": importance,
                "vector": vectors[i] if BATCH_SAVE else None
            }
            if extra_meta:
                meta.update(extra_meta[i])
            self.metadata.append(meta)

        self.index.add(vectors)
        self._save()

    # -------------------------
    # Search with decay & importance
    # -------------------------
    def search(self, query: str, k: int = 5):
        if self.index is None or len(self.metadata) == 0:
            return []

        query_vector = self._embed_batch([query])
        scores, indices = self.index.search(query_vector, k * 3)

        now = time.time()
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            age = now - meta["timestamp"]
            decay = np.exp(-DECAY_LAMBDA * age)
            final_score = float(score) * decay * meta.get("importance", 1.0)
            results.append((final_score, meta))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:k]]