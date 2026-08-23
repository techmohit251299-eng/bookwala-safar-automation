"""
Step 1: Auto-select today's book.

Reads data/books.json, picks the first book not yet marked "used",
marks it used, and writes data/selected_book.json so the next steps
(script generation, TTS, visuals...) know what to work on.

When every book has been used, the whole list resets so the cycle
repeats instead of the pipeline running out of books.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BOOKS_FILE = DATA_DIR / "books.json"
SELECTED_FILE = DATA_DIR / "selected_book.json"


def load_books():
    with open(BOOKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_books(books):
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)


def select_book(books):
    unused = [b for b in books if not b["used"]]

    if not unused:
        # Every book has been used — reset the cycle and start over.
        for b in books:
            b["used"] = False
        unused = books

    # Simple rule for now: first unused book in the list.
    # (Step 2+ can swap this for an LLM call that picks based on
    # theme variety, audience feedback, trending topics, etc.)
    chosen = unused[0]
    chosen["used"] = True
    return chosen, books


def main():
    books = load_books()
    chosen, updated_books = select_book(books)

    save_books(updated_books)
    with open(SELECTED_FILE, "w", encoding="utf-8") as f:
        json.dump(chosen, f, indent=2, ensure_ascii=False)

    print(f"Selected book: {chosen['title']} by {chosen['author']}")


if __name__ == "__main__":
    main()
