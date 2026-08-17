from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def load_knowledge() -> str:
    """
    Read all markdown files from the knowledge folder
    and combine them into one context string.
    """

    knowledge = []

    for file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        try:
            title = file.stem.replace("_", " ").title()
            content = file.read_text(encoding="utf-8")

            knowledge.append(
                
                f"""
=========================
{title}
=========================

{content}
"""
            )
        except Exception as e:
            print(f"Error loading {file.name}: {e}")

    return "\n".join(knowledge)