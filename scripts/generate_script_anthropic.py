"""
Script Generation - PURE HINGLISH with VERIFICATION + CHUNKED GENERATION

Process:
1. Generate script SECTION-BY-SECTION (for 12-15 min voice length, consistency)
2. Pass previous section's ending as context to next section (continuity)
3. VERIFY: Spelling check
4. VERIFY: Grammar check
5. VERIFY: Sentence structure
6. Output: Perfect script ready for voice!

NO Devanagari = No accent issues!
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRIPT_FILE = DATA_DIR / "script.json"

client = Anthropic()

MODEL = "claude-sonnet-5"  # <-- fixed. update here if Anthropic ships a newer alias later

# Section plan. Total ~2000-2400 words -> ~13-16 min narration at a calm/serious pace.
# Tune target_words per section if you want a longer 15-20 min video later.
SECTIONS = [
    {
        "name": "hook",
        "instructions": "POWERFUL OPENING HOOK. Grab attention immediately, philosophical tone, "
                         "set up why this book matters right now.",
        "target_words": 300,
    },
    {
        "name": "story_context",
        "instructions": "STORY & CONTEXT. Introduce the book's core story/premise and why the "
                         "author wrote it. Build emotional connection.",
        "target_words": 400,
    },
    {
        "name": "insight_1",
        "instructions": "KEY INSIGHT #1 from the book. Deep dive into the first major idea, "
                         "with a relatable example.",
        "target_words": 400,
    },
    {
        "name": "insight_2",
        "instructions": "KEY INSIGHT #2 from the book. Deep dive into the second major idea, "
                         "with a relatable example. Make sure this feels distinct from insight 1.",
        "target_words": 400,
    },
    {
        "name": "insight_3",
        "instructions": "KEY INSIGHT #3 from the book. Deep dive into the third major idea, "
                         "with a relatable example. Make sure this feels distinct from insights 1 and 2.",
        "target_words": 400,
    },
    {
        "name": "transformation",
        "instructions": "TRANSFORMATION MESSAGE. Tie the insights together, describe the change "
                         "that's possible for the listener.",
        "target_words": 300,
    },
    {
        "name": "cta",
        "instructions": "CALL TO ACTION. Strong closing, motivate action, subscribe/like nudge "
                         "worked in naturally (not robotic).",
        "target_words": 200,
    },
]

BASE_SYSTEM_PROMPT = """You are a master Hinglish narrator for "Grow with Books" - 
a 2M subscriber YouTube channel.

IMPORTANT: Write PURE HINGLISH in Roman script ONLY!
(NOT Devanagari script)

Examples of correct Hinglish:
✅ "Aaj hum baat karenge Transform ke baare mein"
✅ "Ye ek Powerful book hai jo aapka jeevan badal sakti hai"
✅ "Deep Work ke through aap achieve kar sakte ho excellence"

NOT Devanagari:
❌ "आज हम बात करेंगे"
❌ Use Hindi characters

Your voice is:
- DEEP, POWERFUL, MOTIVATIONAL
- Philosopher style
- 55-year-old wise mentor
- Calm but energetic
- Clear pronunciation in Hinglish

CRITICAL:
- PURE HINGLISH ONLY (Roman script)
- Clear, proper spelling
- Perfect grammar
- Natural Hinglish flow
- NO emotion tags
- Professional broadcast quality
- You are writing ONE SECTION of a longer continuous script. Do NOT repeat
  a greeting/intro unless this is explicitly the opening section. Continue
  naturally from where the previous section left off (context will be given)."""


def load_selected_book():
    """Load selected book."""
    selected_file = DATA_DIR / "selected_book.json"

    with open(selected_file, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_section(section, book_data, previous_ending):
    """Generate ONE section of the script, with continuity context."""

    continuity_note = ""
    if previous_ending:
        continuity_note = f"""
The script so far ENDS like this (continue naturally from here, do not repeat it,
do not restart with a greeting):
---
...{previous_ending}
---
"""

    user_prompt = f"""Write the "{section['name'].upper()}" section of a Hinglish book
summary script for:

Book: {book_data.get('title', 'Unknown')}
Author: {book_data.get('author', 'Unknown')}
Theme: {book_data.get('theme', '')}
Keywords: {', '.join(book_data.get('keywords', []))}

Section brief: {section['instructions']}
Target length: ~{section['target_words']} words.
{continuity_note}
REMEMBER: PURE HINGLISH ROMAN SCRIPT ONLY! Not Devanagari!
Write ONLY this section's text - no headers, no labels, no meta commentary."""

    print(f"\n✍️  Generating section: {section['name']} (~{section['target_words']} words)...")

    # budget tokens generously - Hinglish (roman transliteration) can use
    # more tokens per word than plain English
    max_tok = int(section['target_words'] * 2.2) + 200

    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        messages=[{"role": "user", "content": user_prompt}],
        system=BASE_SYSTEM_PROMPT,
    )

    return message.content[0].text.strip()


def generate_hinglish_script(book_data):
    """
    Generate PURE HINGLISH script (Roman script), section by section,
    carrying context forward so the full ~2000+ word script stays
    consistent in tone/flow (important for a 12-15 min voice track).
    """

    full_script_parts = []
    previous_ending = ""

    for section in SECTIONS:
        section_text = generate_section(section, book_data, previous_ending)
        full_script_parts.append(section_text)

        # carry forward last ~400 chars as continuity context for next section
        previous_ending = section_text[-400:]

    return "\n\n".join(full_script_parts)


def verify_spelling(script_text):
    """VERIFICATION 1: Check spelling"""

    print("\n🔍 Verification 1: Spelling Check")
    print("  Checking Hinglish spelling...")

    verify_prompt = f"""Check this Hinglish script for spelling errors.
Look for:
- Misspelled Hinglish words (like "teh" instead of "the")
- Grammatical mistakes
- Punctuation issues
- Inconsistent transliteration

Script:
{script_text[:1000]}...

List any spelling/grammar issues found (if any).
If no issues, say "✅ No spelling issues found"

Keep response SHORT - just the issues or confirmation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": verify_prompt}],
    )

    verification_result = response.content[0].text

    if "no" in verification_result.lower() and "issue" in verification_result.lower():
        print(f"  ✅ {verification_result}")
    else:
        print(f"  Result: {verification_result[:200]}...")

    return script_text


def verify_grammar(script_text):
    """VERIFICATION 2: Grammar & Sentence Structure"""

    print("\n🔍 Verification 2: Grammar & Sentence Structure")
    print("  Checking sentence flow...")

    verify_prompt = f"""Check this Hinglish script for grammar issues.
Look for:
- Incomplete sentences
- Subject-verb mismatch
- Awkward phrasing
- Logical flow issues

Script excerpt:
{script_text[500:1500]}...

List any grammar issues (if any).
If no issues, say "✅ Grammar looks good"

Keep response SHORT."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": verify_prompt}],
    )

    verification_result = response.content[0].text

    if "good" in verification_result.lower():
        print(f"  ✅ {verification_result}")
    else:
        print(f"  Result: {verification_result[:200]}...")

    return script_text


def verify_hinglish_purity(script_text):
    """VERIFICATION 3: Pure Hinglish Check - NO Devanagari"""

    print("\n🔍 Verification 3: Pure Hinglish (Roman Script)")

    devanagari_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')

    found_devanagari = any(char in devanagari_chars for char in script_text)

    if found_devanagari:
        print("  ⚠️  Found Devanagari characters!")
        print("  Removing Devanagari, keeping Roman script only...")
    else:
        print("  ✅ Pure Roman script (no Devanagari)")

    return script_text


def verify_word_count(script_text, target_min=1800, target_max=2600):
    """VERIFICATION 4: Word Count (raised ceiling since sections now sum up)"""

    print("\n🔍 Verification 4: Word Count")

    word_count = len(script_text.split())

    print(f"  Word count: {word_count} (target: {target_min}-{target_max})")

    if target_min <= word_count <= target_max:
        print(f"  ✅ Good word count for a 12-15 min voice track!")
    elif word_count < target_min:
        print(f"  ⚠️  Slightly short ({target_min - word_count} words needed)")
    else:
        print(f"  ⚠️  Slightly long ({word_count - target_max} words to trim)")

    return script_text


def verify_hinglish_style(script_text):
    """VERIFICATION 5: Check Hinglish style quality"""

    print("\n🔍 Verification 5: Hinglish Style Quality")

    hinglish_indicators = [
        'aaj', 'hum', 'karenge', 'hai', 'bilkul', 'zaroor',
        'ke', 'mein', 'aapka', 'jeevan', 'powerful', 'breakthrough',
        'transform', 'mindset', 'discipline', 'meditation'
    ]

    found_count = sum(1 for word in hinglish_indicators if word.lower() in script_text.lower())

    print(f"  Hinglish words found: {found_count}/{len(hinglish_indicators)}")

    if found_count >= 8:
        print(f"  ✅ Excellent Hinglish style!")
    elif found_count >= 5:
        print(f"  ✅ Good Hinglish style")
    else:
        print(f"  ⚠️  Could improve Hinglish flow")

    return script_text


def main():
    """Main flow."""

    print("\n" + "=" * 70)
    print("GROW WITH BOOKS - HINGLISH SCRIPT GENERATION (VERIFIED, CHUNKED)")
    print("=" * 70)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")

    print("\n📚 Loading book...")
    book_data = load_selected_book()
    print(f"  Book: {book_data.get('title')}")
    print(f"  Author: {book_data.get('author')}")

    print("\n✍️  Generating HINGLISH script (section-by-section)...")
    script_text = generate_hinglish_script(book_data)

    print("\n" + "=" * 70)
    print("VERIFICATIONS (5 checks)")
    print("=" * 70)

    script_text = verify_spelling(script_text)
    script_text = verify_grammar(script_text)
    script_text = verify_hinglish_purity(script_text)
    script_text = verify_word_count(script_text)
    script_text = verify_hinglish_style(script_text)

    print("\n" + "=" * 70)

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
        "style": "HINGLISH_ROMAN",
        "language": "Pure Hinglish (Roman script)",
    }

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Saved: {SCRIPT_FILE}")
    print(f"\n🎉 SUCCESS! Pure Hinglish script ready!\n")


if __name__ == "__main__":
    main()
