"""
Step 2: Generate the narration script for the selected book.

Reads data/selected_book.json, asks Claude to write a professional,
disciplined-narrator style motivational script with inline emotion
tags for ElevenLabs, and writes data/script.json.

Two modes, controlled by the SCRIPT_MODE env var:
  test  -> ~120 words   (quick end-to-end pipeline testing)
  full  -> ~2400 words  (~15-20 min of narration at ~140-150 wpm)

Emotion tags use ElevenLabs' inline audio-tag format (v3 models),
e.g. [serious], [pause], [inspiring], [intense] — these get spoken
with the matching emotional delivery by the TTS step.
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SELECTED_FILE = DATA_DIR / "selected_book.json"
SCRIPT_FILE = DATA_DIR / "script.json"

WORD_TARGETS = {
    "test": 120,
    "full": 2400,
}

SYSTEM_PROMPT = """You are a professional, disciplined narrator for a Hindi-English \
(Hinglish) motivational book-summary YouTube channel called "Bookwala Safar". \
Your tone: serious, focused, mentor-like — someone teaching a disciplined \
audience, not casual or comedic. Short, punchy sentences. Every section ends \
with a strong takeaway line that hooks the listener into the next part.

Write the narration script for the given book. Requirements:
- Target length: {word_count} words.
- Hinglish (natural mix of Hindi and English, Roman script), matching the \
  channel's audience.
- Focus the script on the book's theme: discipline, focus, mental toughness, \
  small consistent action — whatever fits this specific book.
- Insert inline emotion/delivery tags in square brackets at the right \
  moments for ElevenLabs v3 narration, e.g. [serious], [inspiring], \
  [pause], [intense], [reflective]. Don't overuse them — only where the \
  delivery should genuinely shift.
- Structure: hook opening line -> 2-3 core ideas from the book -> a closing \
  takeaway line that lands hard.
- Output ONLY the script text with inline tags. No headers, no markdown, \
  no explanations.
"""


def load_selected_book():
    with open(SELECTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(book, word_count):
    return (
        f"Book: {book['title']} by {book['author']}\n"
        f"Theme: {book['theme']}\n\n"
        f"Write the narration script now, targeting {word_count} words."
    )


def generate_with_claude(book, word_count):
    """Calls the Claude API. Requires ANTHROPIC_API_KEY to be set."""
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT.format(word_count=word_count),
        messages=[{"role": "user", "content": build_prompt(book, word_count)}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def generate_fallback_demo(book, word_count):
    """
    Offline placeholder so the pipeline can be test-run without an API key
    or network access. Replace with a real Claude call in CI via
    generate_with_claude() once ANTHROPIC_API_KEY is set as a secret.
    """
    return (
        f"[serious] Kitno se milne wali ye kahaani, ek insaan ki soch ko hamesha "
        f"ke liye badal deti hai. [pause] Aaj hum baat karenge {book['title']} ki — "
        f"ek aisi kitaab jo sirf padhne ke liye nahi, balki apne aap ko rebuild "
        f"karne ke liye likhi gayi hai. [inspiring] {book['author']} ne ek seedhi "
        f"si baat samjhayi — {book['theme']}. [intense] Ye koi motivation nahi, ye "
        f"ek discipline hai. [reflective] Aur jo isko samajh gaya, uski zindagi "
        f"dobara waisi nahi rahegi."
    )


def main():
    mode = os.environ.get("SCRIPT_MODE", "test")
    word_count = WORD_TARGETS.get(mode, WORD_TARGETS["test"])

    book = load_selected_book()

    if os.environ.get("ANTHROPIC_API_KEY"):
        script_text = generate_with_claude(book, word_count)
    else:
        script_text = generate_fallback_demo(book, word_count)

    output = {
        "book_title": book["title"],
        "mode": mode,
        "target_words": word_count,
        "script": script_text,
    }

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Script generated ({mode} mode, target {word_count} words):\n")
    print(script_text)


if __name__ == "__main__":
    main()
