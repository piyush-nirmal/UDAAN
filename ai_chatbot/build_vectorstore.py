import faiss
import pickle
from pathlib import Path

from app.chatbot.rag_engine import RAGEngine
from app.chatbot.embeddings import EmbeddingModel

VECTOR_DIR = Path("app/vectorstore")

VECTOR_DIR.mkdir(exist_ok=True)

print("Loading documents...")

rag = RAGEngine()

rag.load_markdown()
rag.load_pdfs()

chunks = rag.split_documents()

print(f"Loaded {len(chunks)} chunks")

texts = [c["text"] for c in chunks]

embedder = EmbeddingModel()

vectors = embedder.encode(texts)

dimension = vectors.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(vectors)

faiss.write_index(index, str(VECTOR_DIR / "faiss.index"))

with open(VECTOR_DIR / "chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("=" * 50)
print("Vector database created successfully!")
print(f"Vectors stored: {index.ntotal}")
print("=" * 50)
