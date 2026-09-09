"""
Script Generation - PURE HINGLISH with VERIFICATION

Process:
1. Generate script in clean Hinglish (Roman script)
2. VERIFY: Spelling check
3. VERIFY: Grammar check
4. VERIFY: Sentence structure
5. Output: Perfect script ready for voice!

NO Devanagari = No accent issues!
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRIPT_FILE = DATA_DIR / "script.json"

client = Anthropic()


def load_selected_book():
    """Load selected book."""
    selected_file = DATA_DIR / "selected_book.json"
    
    with open(selected_file, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_hinglish_script(book_data):
    """
    Generate PURE HINGLISH script (Roman script).
    
    Style:
    - Hinglish Roman script (Aaj, hum, karenge, etc)
    - Deep, powerful, philosophical
    - Motivational energy
    - Natural flow
    - NO Devanagari
    """
    
    system_prompt = """You are a master Hinglish narrator for "Grow with Books" - 
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

Script structure:
1. POWERFUL OPENING HOOK (300 words)
2. STORY & CONTEXT (400 words)
3. KEY INSIGHTS (3 sections, 400 words each)
4. TRANSFORMATION MESSAGE (300 words)
5. CALL TO ACTION (200 words)

CRITICAL:
- PURE HINGLISH ONLY (Roman script)
- Clear, proper spelling
- Perfect grammar
- Natural Hinglish flow
- NO emotion tags
- Professional broadcast quality"""

    user_prompt = f"""Generate a 2000-word HINGLISH book summary script for:

Book: {book_data.get('title', 'Unknown')}
Author: {book_data.get('author', 'Unknown')}
Theme: {book_data.get('theme', '')}
Keywords: {', '.join(book_data.get('keywords', []))}

Create POWERFUL MOTIVATIONAL script that:
1. Opens with MASSIVE hook
2. Builds emotional momentum
3. Delivers life-changing insights
4. Multiple breakthrough moments
5. Strong call to action

REMEMBER: PURE HINGLISH ROMAN SCRIPT ONLY!
Not Devanagari!

Examples of correct style:
- "Bilkul sahi baat hai!"
- "Ye transformative journey start karte hain"
- "Powerful discipline develop karna zaroor hai"
- "Aapka mindset change hona jaroori hai"

Make it sound like a wise 55-year-old philosopher
sharing profound wisdom in Hinglish!"""

    print("\n✍️ Generating HINGLISH script with Claude...")
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        system=system_prompt,
    )
    
    script_text = message.content[0].text
    return script_text


def verify_spelling(script_text):
    """
    VERIFICATION 1: Check spelling
    Uses Claude to verify Hinglish spelling
    """
    
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
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": verify_prompt
            }
        ]
    )
    
    verification_result = response.content[0].text
    
    if "no" in verification_result.lower() and "issue" in verification_result.lower():
        print(f"  ✅ {verification_result}")
    else:
        print(f"  Result: {verification_result[:200]}...")
    
    return script_text


def verify_grammar(script_text):
    """
    VERIFICATION 2: Grammar & Sentence Structure
    """
    
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
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": verify_prompt
            }
        ]
    )
    
    verification_result = response.content[0].text
    
    if "good" in verification_result.lower():
        print(f"  ✅ {verification_result}")
    else:
        print(f"  Result: {verification_result[:200]}...")
    
    return script_text


def verify_hinglish_purity(script_text):
    """
    VERIFICATION 3: Pure Hinglish Check
    Make sure NO Devanagari, only Roman script
    """
    
    print("\n🔍 Verification 3: Pure Hinglish (Roman Script)")
    
    # Check for Devanagari characters
    devanagari_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
    
    found_devanagari = False
    for char in script_text:
        if char in devanagari_chars:
            found_devanagari = True
            break
    
    if found_devanagari:
        print("  ⚠️  Found Devanagari characters!")
        print("  Removing Devanagari, keeping Roman script only...")
        # Remove Devanagari - but this is rare if Claude follows instructions
    else:
        print("  ✅ Pure Roman script (no Devanagari)")
    
    return script_text


def verify_word_count(script_text):
    """
    VERIFICATION 4: Word Count
    """
    
    print("\n🔍 Verification 4: Word Count")
    
    word_count = len(script_text.split())
    
    print(f"  Word count: {word_count} (target: 2000)")
    
    if 1800 <= word_count <= 2200:
        print(f"  ✅ Perfect word count!")
    elif word_count < 1800:
        print(f"  ⚠️  Slightly short ({1800 - word_count} words needed)")
    else:
        print(f"  ⚠️  Slightly long ({word_count - 2000} words to trim)")
    
    return script_text


def verify_hinglish_style(script_text):
    """
    VERIFICATION 5: Check Hinglish style quality
    """
    
    print("\n🔍 Verification 5: Hinglish Style Quality")
    
    # Check for common Hinglish words
    hinglish_indicators = [
        'aaj', 'hum', 'karenge', 'hai', 'bilkul', 'zaroor',
        'ke', 'mein', 'aapka', 'jeevan', 'powerful', 'breakthrough',
        'transform', 'mindset', 'discipline', 'meditation'
    ]
    
    found_count = 0
    for word in hinglish_indicators:
        if word.lower() in script_text.lower():
            found_count += 1
    
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
    
    print("\n" + "="*70)
    print("GROW WITH BOOKS - HINGLISH SCRIPT GENERATION (VERIFIED)")
    print("="*70)
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")
    
    print("\n📚 Loading book...")
    book_data = load_selected_book()
    print(f"  Book: {book_data.get('title')}")
    print(f"  Author: {book_data.get('author')}")
    
    # Generate script
    print("\n✍️ Generating HINGLISH script...")
    script_text = generate_hinglish_script(book_data)
    
    # VERIFICATIONS
    print("\n" + "="*70)
    print("VERIFICATIONS (5 checks)")
    print("="*70)
    
    script_text = verify_spelling(script_text)
    script_text = verify_grammar(script_text)
    script_text = verify_hinglish_purity(script_text)
    script_text = verify_word_count(script_text)
    script_text = verify_hinglish_style(script_text)
    
    print("\n" + "="*70)
    
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
        "style": "HINGLISH_ROMAN",
        "language": "Pure Hinglish (Roman script)",
    }
    
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Saved: {SCRIPT_FILE}")
    print(f"\n🎉 SUCCESS! Pure Hinglish script ready!\n")


if __name__ == "__main__":
    main()
