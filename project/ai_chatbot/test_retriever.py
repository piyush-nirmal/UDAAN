from app.chatbot.retriever import Retriever

retriever = Retriever()

query = input("Ask: ")

results = retriever.search(query)

print("\nBest Matches\n")

for i, r in enumerate(results, 1):
    print("=" * 60)
    print(i)
    print(r["source"])
    print()
    print(r["text"])
    