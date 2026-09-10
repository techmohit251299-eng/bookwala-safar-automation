"""
Script Generation - SMART HINDI/DEVANAGARI

Features:
1. Devanagari script (proper Hindi)
2. English words mixed smartly (where needed)
3. Smart pauses (... for reflection, — for drama)
4. Emotion through content + voice settings
5. AUTO BOOK SELECTION from books.json
6. Quality verification
7. Professional Hinglish delivery
8. Guaranteed "..." at the very start (fixes TTS mispronouncing first word)
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRIPT_FILE = DATA_DIR / "script.json"
BOOKS_FILE = DATA_DIR / "books.json"
SELECTED_BOOK_FILE = DATA_DIR / "selected_book.json"

client = Anthropic()

# Keep this in sync with the Hinglish version - same model everywhere.
MODEL = "claude-sonnet-5"


def extract_text(message):
    """Safely pull the text block out of a Claude response, skipping any
    ThinkingBlock (or other non-text blocks) that may come before it."""
    for block in message.content:
        if block.type == "text":
            return block.text.strip()
    raise ValueError("❌ No text block found in Claude's response!")


def load_selected_book():
    """
    LOAD the book that select_book.py already picked.

    NOTE: Book selection now happens ONLY in scripts/select_book.py, which
    runs as its own step earlier in the GitHub Actions workflow. This
    function just reads that result. It used to also run its own
    auto_select_book() logic here, which caused a bug: every run would
    select TWO books (one in select_book.py, then a second one here) -
    the first book would get marked "used" and skipped without ever
    getting a script/voice generated for it.
    """

    print("\n📚 Loading selected book (chosen by select_book.py)...")

    with open(SELECTED_BOOK_FILE, "r", encoding="utf-8") as f:
        selected_book = json.load(f)

    print(f"  ✅ Loaded: {selected_book.get('title')}")
    print(f"  Author: {selected_book.get('author')}")

    return selected_book


def ensure_starting_pause(script_text):
    """
    Guarantee the script begins with '...' regardless of what Claude wrote.
    This gives the TTS engine a tiny lead-in so the very first real word
    is pronounced correctly (fixes the 'first word mispronounced' issue).
    """
    stripped = script_text.lstrip()
    if stripped.startswith("..."):
        return stripped
    return "... " + stripped


def generate_hindi_devanagari_script(book_data):
    """
    Generate script in DEVANAGARI (proper Hindi) with smart English mixing.

    Style:
    - मुख्य भाषा: Devanagari (proper Hindi)
    - English: Technical terms, names, concepts where needed
    - Pauses: ... for reflection, — for drama
    - Emotion: Through content + voice settings (not tags)
    - Natural flow: Philosophical and deep
    """

    system_prompt = """आप "Grow with Books" के लिए एक master narrator हैं।
यह 2 मिलियन subscribers का YouTube channel है।

भाषा नियम:
✅ मुख्य भाषा: Devanagari (proper Hindi)
✅ Technical terms: English रखो (Transform, Breakthrough, Discipline)
✅ Author names: Original रखो (Viktor Frankl, James Clear)
✅ Book names: Original रखो (Atomic Habits, Deep Work)
✅ Concepts: Hindi में समझाओ, फिर English term दो

Pause indicators (emotion is in voice settings, not tags):
- ... = चिंतन के लिए pause (reflection) — SCRIPT MUST START WITH "..."
- — = नाटकीय pause (dramatic moment)
- ! = शक्तिशाली बिंदु (powerful point)

Script structure:
1. शक्तिशाली Opening Hook (300 शब्द) - MUST begin with "..."
2. कहानी और संदर्भ (400 शब्द)
3. मुख्य Insights (3 sections, 400 शब्द each)
4. रूपांतरण संदेश (300 शब्द)
5. Call to Action (200 शब्द)

Voice सेटिंग्स (emotion के लिए):
- Depth: गहरा, गंभीर
- Power: शक्तिशाली, प्रेरणादायक
- Calm: मापा हुआ, विचारशील
- Age: 55+ साल का दार्शनिक

महत्वपूर्ण:
- NO emotion tags like [serious], [pause]
- Smart pauses only (... and —)
- The very first character(s) of the whole script MUST be "..."
- Professional broadcast quality
- 2M subscriber channel level

English words की spelling (बहुत ज़रूरी):
- English/technical words हमेशा उनकी STANDARD, DICTIONARY-CORRECT spelling में लिखो
  (जैसे "Transform", "Breakthrough", "Discipline", "Mindset")
- कभी भी phonetic, slang, या casual spelling मत use करो
  (गलत: "Transfrom", "Bricthru", "Mindsett" — सही: "Transform", "Breakthrough", "Mindset")
- Hindi/English का mix बिल्कुल natural रहने दो — कोई fixed ratio फॉलो मत करो,
  जो भी sentence में स्वाभाविक लगे वही रखो
- Author names और book titles भी उनकी original/official spelling में ही लिखो, कभी बदलो मत"""

    user_prompt = f"""Generate a 2000-word script in Devanagari (Hindi) with smart English mixing:

Book: {book_data.get('title', 'Unknown')}
Author: {book_data.get('author', 'Unknown')}
Theme: {book_data.get('theme', '')}
Keywords: {', '.join(book_data.get('keywords', []))}

Create POWERFUL MOTIVATIONAL script that:
1. Opens with MASSIVE hook - the FIRST thing written must be "..." before the first word
2. Builds emotional momentum (through content, not tags)
3. Delivers life-changing insights
4. Multiple breakthrough moments
5. Strong call to action

Hindi/Devanagari Example:
"... आज हम बात करेंगे Transform के बारे में...
यह एक powerful book है जो आपके जीवन को बदल सकती है।
Deep Work के माध्यम से आप excellence achieve कर सकते हैं!"

Style: गहरा, दार्शनिक, प्रेरणादायक (Deep, philosophical, motivational)
Tone: 55 साल का wise mentor जो profound wisdom शेयर कर रहा है

Remember: मुख्य Hindi + Smart English + Natural pauses + MUST start with "..."!"""

    print("\n✍️ Generating Devanagari script with Claude...")

    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        system=system_prompt,
    )

    script_text = extract_text(message)
    script_text = ensure_starting_pause(script_text)
    return script_text


def verify_hindi_quality(script_text):
    """
    VERIFICATION 1: Check Hindi script quality
    """

    print("\n🔍 Verification 1: Hindi Script Quality")
    print("  Checking Devanagari and content flow...")

    verify_prompt = f"""इस Hindi script को check करो:

Script excerpt:
{script_text[:1000]}...

Check करो:
1. Hindi की spelling सही है?
2. Sentences complete हैं?
3. English words सही जगह हैं?
4. Flow natural है?

कोई issues मिले तो बताओ, नहीं तो "✅ Script quality अच्छी है" कहो।

SHORT response दो।"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": verify_prompt
            }
        ]
    )

    verification_result = extract_text(response)
    print(f"  Result: {verification_result[:300]}...")

    return script_text


def verify_emotional_depth(script_text):
    """
    VERIFICATION 2: Check emotional depth and engagement
    """

    print("\n🔍 Verification 2: Emotional Depth & Engagement")
    print("  Checking content for emotional impact...")

    verify_prompt = f"""इस script में emotional depth check करो:

Script excerpt:
{script_text[500:1500]}...

Check करो:
1. कहानी engaging है?
2. Powerful moments हैं?
3. Breakthrough insights हैं?
4. Motivation present है?

Scale: 1-10 में score दो। 8+ अच्छा है।

SHORT response।"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": verify_prompt
            }
        ]
    )

    verification_result = extract_text(response)
    print(f"  Result: {verification_result[:300]}...")

    return script_text


def verify_word_count(script_text):
    """
    VERIFICATION 3: Word count
    """

    print("\n🔍 Verification 3: Word Count & Length")

    # Count Devanagari words (simpler count)
    word_count = len(script_text.split())

    print(f"  Words: {word_count} (target: 2000)")

    if 1800 <= word_count <= 2200:
        print(f"  ✅ Perfect!")
    elif word_count < 1800:
        print(f"  ⚠️  Slightly short")
    else:
        print(f"  ⚠️  Slightly long")

    return script_text


def verify_pause_flow(script_text):
    """
    VERIFICATION 4: Smart pause usage
    """

    print("\n🔍 Verification 4: Pause & Flow Quality")

    ellipsis_count = script_text.count('...')
    em_dash_count = script_text.count('—')
    exclamation_count = script_text.count('!')
    starts_with_pause = script_text.lstrip().startswith("...")

    print(f"  Starts with '...': {'✅' if starts_with_pause else '❌'}")
    print(f"  Reflection pauses (...): {ellipsis_count}")
    print(f"  Dramatic pauses (—): {em_dash_count}")
    print(f"  Power moments (!): {exclamation_count}")

    total_pauses = ellipsis_count + em_dash_count + exclamation_count

    if total_pauses >= 8:
        print(f"  ✅ Excellent pacing! ({total_pauses} pause markers)")
    elif total_pauses >= 5:
        print(f"  ✅ Good pacing ({total_pauses} pause markers)")
    else:
        print(f"  ⚠️  Could add more pauses")

    return script_text


def main():
    """Main flow."""

    print("\n" + "=" * 70)
    print("GROW WITH BOOKS - DEVANAGARI SCRIPT (AUTO BOOK SELECT)")
    print("=" * 70)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")

    # AUTO-SELECT BOOK
    book_data = load_selected_book()

    # Generate script
    print("\n✍️ Generating Devanagari script with emotion...")
    script_text = generate_hindi_devanagari_script(book_data)

    # Verifications
    print("\n" + "=" * 70)
    print("QUALITY VERIFICATIONS (4 checks)")
    print("=" * 70)

    script_text = verify_hindi_quality(script_text)
    script_text = verify_emotional_depth(script_text)
    script_text = verify_word_count(script_text)
    script_text = verify_pause_flow(script_text)

    print("\n" + "=" * 70)

    # Save
    print("\n💾 Saving script...")

    output_data = {
        "book": book_data.get('title'),
        "author": book_data.get('author'),
        "theme": book_data.get('theme', ''),
        "keywords": book_data.get('keywords', []),
        "hashtags": book_data.get('hashtags', ''),
        "script": script_text,
        "word_count": len(script_text.split()),
        "character_count": len(script_text),
        "style": "DEVANAGARI_WITH_ENGLISH",
        "language": "Devanagari (Hindi) with smart English",
        "emotion_handling": "Content-based + Voice settings",
    }

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Saved: {SCRIPT_FILE}")
    print(f"  ✅ Selected: {SELECTED_BOOK_FILE}")
    print(f"\n🎉 SUCCESS! Devanagari script with auto book selection ready!\n")


if __name__ == "__main__":
    main()
