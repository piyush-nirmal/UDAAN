from app.chatbot.rag_engine import RAGEngine

rag = RAGEngine()

rag.load_markdown()
rag.load_pdfs()

print("Loaded Documents:")
for doc in rag.documents:
    print(doc["source"], "->", len(doc["text"]))
    
chunks = rag.split_documents()

print("=" * 50)
print("Documents Loaded:", len(rag.documents))
print("Chunks Created:", len(chunks))
print("=" * 50)

for chunk in chunks[:5]:
    print(chunk["source"])
    print(chunk["text"][:200])
    print("-" * 50)