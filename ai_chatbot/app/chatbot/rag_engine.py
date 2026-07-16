from pathlib import Path
from pypdf import PdfReader

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"


class RAGEngine:

    def __init__(self):
        self.documents = []

    def load_markdown(self):
        """Load all markdown files."""

        for file in KNOWLEDGE_DIR.glob("*.md"):

            with open(file, "r", encoding="utf-8") as f:

                self.documents.append({
                    "source": file.name,
                    "text": f.read()
                })

    def load_pdfs(self):
        """Load all uploaded PDFs."""

        for file in UPLOAD_DIR.glob("*.pdf"):

            reader = PdfReader(file)

            text = ""

            for page in reader.pages:
                extracted = page.extract_text()

                if extracted:
                    text += extracted + "\n"

            self.documents.append({
                "source": file.name,
                "text": text
            })

    def split_documents(self, chunk_size=700, overlap=100):
        """
        Split every document into overlapping chunks.
        """

        chunks = []

        for doc in self.documents:

            text = doc["text"]

            start = 0

            while start < len(text):

                end = start + chunk_size

                chunk = text[start:end]

                chunks.append({
                    "source": doc["source"],
                    "text": chunk
                })

                start += chunk_size - overlap

        return chunks