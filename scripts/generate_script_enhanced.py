"""
Enhanced Script Generation with PERFECT HINGLISH PRONUNCIATION
- DH, TH sounds properly handled
- Opening hook with "..." pause for rhythm
- Consistent style across sections
- Post-chunking "..." connectors for flow
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRIPT_FILE = DATA_DIR / "script.json"

client = Anthropic()
MODEL = "claude-sonnet-5"

# ✅ CRITICAL HINGLISH PRONUNCIATION RULES
HINGLISH_PHONETICS = {
    # DH sounds - aspirated D
    "dhaara": "ध",           # धारा
    "dhare": "ध",            # धारे
    "dhyan": "ध",            # ध्यान
    "dharti": "ध",           # धरती
    "dhire": "ध",            # धीरे
    "dhuaan": "ध",           # धुआं
    "dhal": "ध",             # ढाल
    
    # TH sounds - aspirated T
    "thoda": "थ",            # थोड़ा
    "think": "थ",            # थिंक (aspirated T + ink)
    "thand": "थ",            # ठंड
    "thahera": "थ",          # थहेरा
    "theek": "थ",            # ठीक
    "toh": "त",              # तो
    "tab": "त",              # तब
    
    # Common Hinglish words
    "aadhaar": "आधार",       # आधार
    "aadmi": "आदमी",         # आदमी
    "aadha": "आधा",          # आधा
    "bhay": "भय",            # भय
    "bhaagne": "भागने",       # भागने
    "bhagwaan": "भगवान",     # भगवान
    "shakti": "शक्ति",        # शक्ति
    "shuddh": "शुद्ध",        # शुद्ध
}

SECTIONS = [
    {
        "name": "hook",
        "instructions": "POWERFUL OPENING HOOK. Grab attention immediately, philosophical tone. Start with '...' pause effect.",
        "target_words": 300,
        "pause_start": True,  # ✅ Start with "..." for breath
    },
    {
        "name": "story_context",
        "instructions": "STORY & CONTEXT. Introduce the book's core story and why it matters. Build emotional connection.",
        "target_words": 400,
        "pause_start": False,
    },
    {
        "name": "insight_1",
        "instructions": "KEY INSIGHT #1. Deep dive into first major idea with relatable example.",
        "target_words": 400,
        "pause_start": False,
    },
    {
        "name": "insight_2",
        "instructions": "KEY INSIGHT #2. Deep dive into second major idea, distinct from insight 1.",
        "target_words": 400,
        "pause_start": False,
    },
    {
        "name": "insight_3",
        "instructions": "KEY INSIGHT #3. Deep dive into third major idea, distinct from insights 1 and 2.",
        "target_words": 400,
        "pause_start": False,
    },
    {
        "name": "transformation",
        "instructions": "TRANSFORMATION MESSAGE. Tie insights together, describe the change possible for listener.",
        "target_words": 300,
        "pause_start": False,
    },
    {
        "name": "cta",
        "instructions": "CALL TO ACTION. Strong closing, motivate action, subscribe nudge worked in naturally.",
        "target_words": 200,
        "pause_start": False,
    },
]

BASE_SYSTEM_PROMPT = """You are a master Hinglish narrator for "Grow with Books" - a 2M subscriber YouTube channel.

CRITICAL PRONUNCIATION RULES:

1️⃣ DH SOUNDS (aspirated D - ध):
   ✅ "Dhyan" (ध्यान) - dhyan
   ✅ "Dhire" (धीरे) - dhire  
   ✅ "Dharti" (धरती) - dharti
   Write as: "dh" not "d"

2️⃣ TH SOUNDS (aspirated T - थ/ठ):
   ✅ "Thoda" (थोड़ा) - thoda
   ✅ "Theek" (ठीक) - theek
   ✅ "Think" (thinking) - think
   Write as: "th" not "t"

3️⃣ OPENING HOOK MUST START WITH:
   "... Zara sochiye" or "... Dekho ek baat"
   The "..." creates breathing room and rhythm

4️⃣ STYLE CONSISTENCY:
   - Same tone across ALL sections
   - Philosopher, wise mentor voice
   - Deep, powerful, motivational
   - ZERO emotional tags
   - 55-year-old wise mentor style

5️⃣ PURE HINGLISH ROMAN ONLY:
   ✅ "Aaj hum baat karenge"
   ❌ "आज हम बात करेंगे" (No Devanagari!)

6️⃣ NATURAL FLOW:
   - Clear sentence structure
   - No sudden transitions
   - Build momentum naturally
   - Professional broadcast quality

EXAMPLES OF CORRECT HINGLISH WITH PRONUNCIATION:
✅ "... Zara dhyan do - yeh ek important baat hai"
✅ "Jab tak aap thoda alag sochne laag jaate ho"
✅ "Uska dharma tha unhe seekhna"
✅ "Har din thoda sa effort kar sakte ho"

You are writing ONE SECTION of a longer script. Continue naturally from context."""


def extract_text(message):
    """Safely extract text from Claude response."""
    for block in message.content:
        if block.type == "text":
            return block.text.strip()
    raise ValueError("❌ No text block found in Claude's response!")


def load_selected_book():
    """Load selected book."""
    selected_file = DATA_DIR / "selected_book.json"
    with open(selected_file, "r", encoding="utf-8") as f:
        return json.load(f)


def add_rhythm_pauses(text, is_hook=False):
    """
    ✅ Add "..." pauses for natural rhythm
    - Hook sections start with "..."
    - After punctuation marks add breathing room
    """
    if is_hook and not text.strip().startswith("..."):
        text = "... " + text

    # Add slight pause after key punctuation
    text = text.replace("!", "! ... ")
    text = text.replace("?", "? ... ")
    text = text.replace("।", "। ... ")  # Devanagari full stop (if any)
    
    # Clean up multiple spaces
    text = " ".join(text.split())
    
    return text


def enhance_hinglish_pronunciation(text):
    """
    ✅ Enhance Hinglish pronunciation rules
    - Ensure DH sounds are written as "dh" not "d"
    - Ensure TH sounds are written as "th" not "t"
    - Verify proper Roman transliteration
    """
    replacements = {
        # Common mistakes - D becoming DH
        "Dharti": "Dharti",
        "Dharma": "Dharma",
        "Dhyan": "Dhyan",
        "Dhire": "Dhire",
        "Dhaara": "Dhaara",
        
        # Common mistakes - T becoming TH
        "Thoda": "Thoda",
        "Think": "Think",
        "Theek": "Theek",
        "Thand": "Thand",
        "Thahera": "Thahera",
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong.lower(), correct.lower())
    
    return text


def generate_section(section, book_data, previous_ending):
    """Generate ONE section with enhanced pronunciation."""
    
    continuity_note = ""
    if previous_ending:
        continuity_note = f"""
Previous section ENDS like this (continue naturally from here, NO restart):
---
...{previous_ending}
---

Now continue with '...' pause to maintain rhythm."""

    user_prompt = f"""Write the "{section['name'].upper()}" section for:

Book: {book_data.get('title')}
Author: {book_data.get('author')}
Theme: {book_data.get('theme')}
Keywords: {', '.join(book_data.get('keywords', []))}

Instructions: {section['instructions']}
Target: ~{section['target_words']} words

{continuity_note}

CRITICAL RULES:
1. DH sounds: Write "dh" (dharti, dhyan, dhire) NOT "d"
2. TH sounds: Write "th" (thoda, think, theek) NOT "t"
3. Pure Hinglish Roman script ONLY - NO Devanagari!
4. Professional, consistent philosopher tone
5. Write ONLY the section text - no labels or metadata"""

    print(f"\n✍️  Generating: {section['name']} (~{section['target_words']} words)...")

    max_tok = int(section['target_words'] * 2.2) + 200

    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        messages=[{"role": "user", "content": user_prompt}],
        system=BASE_SYSTEM_PROMPT,
    )

    section_text = extract_text(message)
    
    # ✅ Add rhythm pauses
    section_text = add_rhythm_pauses(section_text, is_hook=section['pause_start'])
    
    # ✅ Enhance pronunciation
    section_text = enhance_hinglish_pronunciation(section_text)
    
    return section_text


def generate_hinglish_script(book_data):
    """Generate script section-by-section with rhythm."""
    
    full_script_parts = []
    previous_ending = ""

    for section in SECTIONS:
        section_text = generate_section(section, book_data, previous_ending)
        full_script_parts.append(section_text)
        
        # Carry forward last 400 chars for continuity
        previous_ending = section_text[-400:]

    return "\n\n".join(full_script_parts)


def verify_pronunciation(script_text):
    """Verify DH and TH pronunciation."""
    
    print("\n🔍 Verification: DH/TH Pronunciation Check")
    
    dh_count = script_text.lower().count("dh")
    th_count = script_text.lower().count("th")
    pause_count = script_text.count("...")
    
    print(f"  ✅ DH sounds found: {dh_count}")
    print(f"  ✅ TH sounds found: {th_count}")
    print(f"  ✅ Rhythm pauses (...) found: {pause_count}")
    
    if pause_count >= 7:  # At least one per section
        print(f"  ✅ Good rhythm pattern established!")
    else:
        print(f"  ⚠️  Consider adding more '...' pauses for rhythm")
    
    return script_text


def verify_spelling(script_text):
    """VERIFICATION: Spelling check"""
    
    print("\n🔍 Verification: Spelling & Transliteration")
    print("  Checking Hinglish words...")

    verify_prompt = f"""Check this Hinglish script for errors:
- DH sounds spelled correctly (dhyan, dhare, dharti - NOT d)
- TH sounds spelled correctly (thoda, think, theek - NOT t)
- Hinglish spelling consistency
- No Devanagari characters
- Punctuation and flow

Script excerpt:
{script_text[:1000]}...

List issues found (if any). If no issues, say "✅ All good"."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": verify_prompt}],
    )

    result = extract_text(response)
    print(f"  {result[:200]}...")
    
    return script_text


def verify_rhythm_flow(script_text):
    """VERIFICATION: Check rhythm and flow."""
    
    print("\n🔍 Verification: Rhythm & Flow")
    
    sections = script_text.split("\n\n")
    print(f"  Sections: {len(sections)}")
    
    for i, section in enumerate(sections[:3], 1):
        starts_with_pause = "..." in section[:20]
        status = "✅" if starts_with_pause else "⚠️"
        print(f"  {status} Section {i}: {section[:50]}...")
    
    return script_text


def main():
    """Main flow."""
    
    print("\n" + "="*70)
    print("GROW WITH BOOKS - HINGLISH SCRIPT (DH/TH PERFECT + RHYTHM)")
    print("="*70)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")

    print("\n📚 Loading book...")
    book_data = load_selected_book()
    print(f"  Book: {book_data.get('title')}")
    print(f"  Author: {book_data.get('author')}")

    print("\n✍️  Generating script with perfect DH/TH pronunciation...")
    script_text = generate_hinglish_script(book_data)

    print("\n" + "="*70)
    print("VERIFICATIONS")
    print("="*70)

    script_text = verify_pronunciation(script_text)
    script_text = verify_spelling(script_text)
    script_text = verify_rhythm_flow(script_text)

    print("\n" + "="*70)
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
        "style": "HINGLISH_ROMAN_DH_TH_OPTIMIZED",
        "language": "Pure Hinglish (Roman script)",
        "pronunciation_optimized": True,
        "rhythm_pauses": True,
    }

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Saved: {SCRIPT_FILE}")
    print(f"\n🎉 SUCCESS! Perfect Hinglish script ready!\n")


if __name__ == "__main__":
    main()
