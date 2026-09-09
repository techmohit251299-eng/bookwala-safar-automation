"""
Script Generation - MOTIVATIONAL with Energy Cues

Strategy:
1. Add MOTIVATIONAL keywords naturally
2. Use punctuation for pacing (!!!, ..., —)
3. NO tags that get read literally
4. Energy signals through content
5. Powerful yet clean delivery
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


def generate_motivational_script(book_data):
    """
    Generate POWERFUL MOTIVATIONAL script WITHOUT emotion tags.
    Uses punctuation and keywords for energy.
    """
    
    system_prompt = """You are an elite motivational narrator for "Grow with Books" - 
a YouTube channel with 2M subscribers. Your voice is:

- POWERFUL, PASSIONATE, MOTIVATIONAL
- Deep, transformational insights
- ENERGETIC but not frantic
- Clean, powerful Hinglish
- Natural pacing through punctuation

Script structure:
1. POWERFUL hook (grab attention)
2. Build story arc (create momentum)
3. KEY insights (transformational moments)
4. CALL TO ACTION (inspire change)

ENERGY SIGNALS (NO TAGS):
- Use ??? for emphasis points
- Use — for pause moments
- Use ... for reflection
- Use exclamation! for power
- Use bold keywords for motivation

Create 2000-word script with:
- Motivational keywords: Transform, Powerful, Breakthrough, Unlock, Master, Unleash
- Building energy arc (starts strong, builds higher)
- Multiple payoff moments
- Clear call to action
- Hinglish natural delivery

NO emotion tags like [serious] or [pause] - use punctuation instead!"""

    user_prompt = f"""Generate a 2000-word MOTIVATIONAL Hinglish book summary for:

Book: {book_data.get('title', 'Unknown')}
Author: {book_data.get('author', 'Unknown')}
Theme: {book_data.get('theme', '')}
Keywords: {', '.join(book_data.get('keywords', []))}

Create a POWERFUL script that:
1. Opens with MASSIVE hook (grab attention immediately!)
2. Builds emotional momentum (story arc)
3. Delivers life-changing insights
4. Multiple powerful moments
5. Strong closing that inspires action

Use natural punctuation for pacing:
- ??? for emphasis
- — for dramatic pauses
- ... for reflection
- ! for power moments

Make it sound like a powerful mentor sharing breakthrough wisdom!
NO emotion tags - pure clean powerful delivery!"""

    print("\n✍️  Generating MOTIVATIONAL script with Claude...")
    
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


def clean_script_tags(script_text):
    """
    Clean any emotion tags that might sneak in.
    But keep punctuation-based energy signals.
    """
    
    print("\n🧹 Cleaning literal emotion tags...")
    
    # Remove tags that would be read literally
    tags_to_remove = {
        '[serious]': '',
        '[excited]': '',
        '[motivated]': '',
        '[pause]': '...',
        '[long pause]': '—',
        '[emphasis]': '',
        '[dramatic]': '',
        '[powerful]': '',
    }
    
    cleaned_count = 0
    
    for tag, replacement in tags_to_remove.items():
        if tag in script_text:
            script_text = script_text.replace(tag, replacement)
            cleaned_count += 1
            print(f"  ✓ Removed: {tag}")
    
    if cleaned_count == 0:
        print(f"  ✓ No literal tags found (clean!)")
    
    return script_text


def verify_motivational_energy(script_text):
    """
    Verify script has motivational energy.
    Check for power keywords and pacing signals.
    """
    
    print("\n🔍 Verification: Motivational Energy")
    
    # Power keywords
    power_keywords = [
        'transform', 'powerful', 'breakthrough', 'unlock', 'master',
        'unleash', 'incredible', 'amazing', 'revolutionary', 'life-changing'
    ]
    
    power_words_found = 0
    for keyword in power_keywords:
        if keyword.lower() in script_text.lower():
            power_words_found += 1
    
    print(f"  ✅ Power keywords found: {power_words_found}/10")
    
    # Energy punctuation
    exclamations = script_text.count('!')
    em_dashes = script_text.count('—')
    ellipsis = script_text.count('...')
    questions = script_text.count('?')
    
    print(f"  ✅ Energy markers:")
    print(f"     - Exclamation (!): {exclamations}")
    print(f"     - Em dash (—): {em_dashes}")
    print(f"     - Ellipsis (...): {ellipsis}")
    print(f"     - Questions (?): {questions}")
    
    total_energy = exclamations + em_dashes + ellipsis + questions
    
    if total_energy > 10:
        print(f"  ✅ EXCELLENT motivational pacing! ({total_energy} energy markers)")
    elif total_energy > 5:
        print(f"  ✅ GOOD motivational energy ({total_energy} markers)")
    else:
        print(f"  ⚠️  Could add more energy markers ({total_energy})")
    
    print()
    
    return script_text


def verify_word_count(script_text):
    """Check word count."""
    
    print("🔍 Verification: Word Count")
    
    word_count = len(script_text.split())
    char_count = len(script_text)
    
    print(f"  Words: {word_count} (target: 2000)")
    print(f"  Chars: {char_count}")
    
    if 1800 <= word_count <= 2200:
        print(f"  ✅ Perfect!\n")
    else:
        print(f"  ⚠️  Adjust length\n")
    
    return script_text


def main():
    """Main."""
    
    print("\n" + "="*70)
    print("GROW WITH BOOKS - MOTIVATIONAL SCRIPT GENERATION")
    print("="*70)
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")
    
    print("\n📚 Loading book...")
    book_data = load_selected_book()
    print(f"  Book: {book_data.get('title')}")
    print(f"  Author: {book_data.get('author')}")
    
    # Generate
    script_text = generate_motivational_script(book_data)
    
    # Clean
    script_text = clean_script_tags(script_text)
    
    # Verify
    print("\n🔍 VERIFICATIONS:")
    print("━"*70)
    script_text = verify_motivational_energy(script_text)
    script_text = verify_word_count(script_text)
    print("━"*70)
    
    # Save
    print("💾 Saving script...")
    
    output_data = {
        "book": book_data.get('title'),
        "author": book_data.get('author'),
        "theme": book_data.get('theme', ''),
        "keywords": book_data.get('keywords', []),
        "hashtags": book_data.get('hashtags', ''),
        "script": script_text,
        "word_count": len(script_text.split()),
        "character_count": len(script_text),
        "style": "MOTIVATIONAL",
    }
    
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ Saved: {SCRIPT_FILE}")
    print(f"\n🎉 SUCCESS! Motivational script ready!\n")


if __name__ == "__main__":
    main()
