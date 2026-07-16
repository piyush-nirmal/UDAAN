import pickle
from pathlib import Path

import faiss

from app.chatbot.embeddings import EmbeddingModel


class Retriever:

    def __init__(self):
        vector_dir = Path(__file__).parent.parent / "vectorstore"

        self.index = faiss.read_index(str(vector_dir / "faiss.index"))

        with open(vector_dir / "chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)

        self.embedder = EmbeddingModel()

    def search(self, query, k=3):

        vector = self.embedder.encode([query])

        scores, indices = self.index.search(vector, k)

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            chunk = self.chunks[idx]

            results.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "score": float(score)
            })

            return results