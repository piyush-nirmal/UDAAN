from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


class KnowledgeRetriever:

    def __init__(self):
        self.documents = {}
        self.load_documents()

    def load_documents(self):
        """Load every markdown file."""

        self.documents.clear()

        for file in KNOWLEDGE_DIR.glob("*.md"):
            with open(file, "r", encoding="utf-8") as f:
                self.documents[file.stem] = f.read()

    def search(self, query, top_k=3):
        """
        Simple keyword search.
        """

        query = query.lower()

        scores = []

        for name, text in self.documents.items():

            score = 0

            lower = text.lower()

            for word in query.split():

                score += lower.count(word)

            scores.append((score, text))

        scores.sort(reverse=True)

        results = []

        for score, text in scores[:top_k]:

            if score > 0:
                results.append(text)

        print("\n===== KNOWLEDGE RETRIEVAL =====")

        for score, text in scores[:top_k]:
            print(f"Score: {score}")

        print("===============================\n")
        return "\n\n".join(results)