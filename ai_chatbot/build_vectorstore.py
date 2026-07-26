import pickle
from pathlib import Path

import faiss

from app.chatbot.embeddings import EmbeddingModel
from app.chatbot.rag_engine import RAGEngine
from app.chatbot.django_loader import DjangoKnowledgeLoader
from app.chatbot.html_loader import HTMLKnowledgeLoader

VECTOR_DIR = Path("app/vectorstore")
VECTOR_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("Loading knowledge from Django...")
print("=" * 60)

django_loader = DjangoKnowledgeLoader()
django_docs = django_loader.load_everything()

print(f"Django Documents : {len(django_docs)}")

print("\n" + "=" * 60)
print("Loading knowledge from HTML pages...")
print("=" * 60)

html_loader = HTMLKnowledgeLoader()
html_docs = html_loader.load_pages()

print(f"HTML Pages : {len(html_docs)}")

# ----------------------------------------------------
# Merge all knowledge
# ----------------------------------------------------

documents = django_docs + html_docs

print("\n" + "=" * 60)
print(f"Total Knowledge Documents : {len(documents)}")
print("=" * 60)

# ----------------------------------------------------
# Chunking
# ----------------------------------------------------

rag = RAGEngine()
rag.documents = documents

chunks = rag.split_documents()

print(f"Created {len(chunks)} chunks")

# ----------------------------------------------------
# Embeddings
# ----------------------------------------------------

print("\nLoading embedding model...")

embedder = EmbeddingModel()

texts = [chunk["text"] for chunk in chunks]

vectors = embedder.encode(texts)

dimension = vectors.shape[1]

# Inner Product (Cosine Similarity if vectors are normalized)
index = faiss.IndexFlatIP(dimension)

index.add(vectors)

# ----------------------------------------------------
# Save Vector Database
# ----------------------------------------------------

faiss.write_index(index, str(VECTOR_DIR / "faiss.index"))

with open(VECTOR_DIR / "chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("\n" + "=" * 60)
print("✅ Vector Database Built Successfully")
print("=" * 60)
print(f"Django Docs : {len(django_docs)}")
print(f"HTML Docs   : {len(html_docs)}")
print(f"Total Docs  : {len(documents)}")
print(f"Chunks      : {len(chunks)}")
print(f"Vectors     : {index.ntotal}")
print("=" * 60)