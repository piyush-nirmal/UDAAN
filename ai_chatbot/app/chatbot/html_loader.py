from pathlib import Path
from bs4 import BeautifulSoup
import re


class HTMLKnowledgeLoader:

    def __init__(self):
        # Django templates folder
        self.template_dir = (
            Path(__file__).resolve().parents[3] / "templates"
        )

        # Only index useful public pages
        self.pages = [
            "home.html",
            "aboutus.html",
            "ourmission_values.html",
            "faq.html",
            "contact_us.html",
            "volunteering.html",
            "our_team.html",
            "resources.html",
            "our_policies.html",
            "career_and_fellowship.html",
            "blood_donation.html",
        ]

    def load_pages(self):


        documents = []

        for page in self.pages:

            file = self.template_dir / page

            if not file.exists():
                print(f"Skipped: {page}")
                continue

            with open(file, "r", encoding="utf-8") as f:
                html = f.read()

            # Remove Django template tags BEFORE parsing
            html = re.sub(r"{%.*?%}", "", html, flags=re.DOTALL)
            html = re.sub(r"{{.*?}}", "", html, flags=re.DOTALL)

            soup = BeautifulSoup(html, "html.parser")

            # Remove unwanted tags
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n")

            lines = []

            for line in text.splitlines():

                line = line.strip()

                if not line:
                    continue

                # Skip very short menu/button text
                if len(line) <= 2:
                    continue

                # Skip Django leftovers
                if line.startswith("{") or line.startswith("%"):
                    continue

                lines.append(line)

            clean_text = "\n".join(lines)

            # Remove repeated blank lines
            clean_text = re.sub(r"\n{2,}", "\n", clean_text)

            documents.append({
                "source": "HTML",
                "title": page.replace(".html", ""), 
                "text": clean_text
            })

        return documents


    
if __name__ == "__main__":

        loader = HTMLKnowledgeLoader()

        docs = loader.load_pages()

        print(f"\nLoaded {len(docs)} HTML pages\n")

        for doc in docs:

            print("=" * 60)
            print(doc["title"])
            print(doc["text"][:500])