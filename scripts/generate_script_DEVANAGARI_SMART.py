"""
Script Generation - SMART HINDI/DEVANAGARI (CHUNKED, for full 12-15 min length)

Features:
1. Devanagari script (proper Hindi)
2. English words mixed smartly (where needed), always standard/correct spelling
3. Smart pauses (... for reflection, — for drama)
4. Emotion through content + voice settings
5. Book is LOADED from selected_book.json (select_book.py already chose it)
6. Quality verification
7. Guaranteed "..." at the very start (fixes TTS mispronouncing first word)
8. SECTION-BY-SECTION generation (like the Hinglish version) - this is the
   fix for scripts coming out too short: Devanagari text uses far more
   tokens per word than Roman/English text, so asking for a whole ~2000-word
   script in ONE Claude call with a small max_tokens budget was cutting the
   script off early (that's why voice.mp3 was only ~5 min instead of 12-15).
   Generating section-by-section gives each part its own generous token
   budget, and stitches them together with continuity context.
9. Channel name ("Grow with Books") is explicitly welcomed near the start
   of the hook section.
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRIPT_FILE = DATA_DIR / "script.json"
SELECTED_BOOK_FILE = DATA_DIR / "selected_book.json"

client = Anthropic()

# Keep this in sync with the Hinglish version - same model everywhere.
MODEL = "claude-sonnet-5"

CHANNEL_NAME = "Grow with Books"

# Section plan. Total ~2200-2600 words -> ~13-16 min narration at a calm/
# serious pace, matching the target the Hinglish version uses.
SECTIONS = [
    {
        "name": "hook",
        "instructions": (
            "शक्तिशाली OPENING HOOK। सबसे पहले दर्शकों का ध्यान खींचो, फिर चैनल "
            f'का नाम "{CHANNEL_NAME}" का गर्मजोशी से स्वागत करते हुए ज़िक्र करो '
            "(जैसे: 'आपका स्वागत है Grow with Books में')। इसके बाद philosophical "
            "tone में बताओ कि यह किताब अभी क्यों महत्वपूर्ण है।"
        ),
        "target_words": 320,
    },
    {
        "name": "story_context",
        "instructions": (
            "कहानी और संदर्भ। किताब की मुख्य कहानी/premise से परिचय कराओ और बताओ "
            "लेखक ने यह क्यों लिखी। Emotional connection बनाओ।"
        ),
        "target_words": 420,
    },
    {
        "name": "insight_1",
        "instructions": (
            "मुख्य INSIGHT #1। किताब के पहले बड़े विचार पर गहराई से बात करो, "
            "एक relatable example के साथ।"
        ),
        "target_words": 420,
    },
    {
        "name": "insight_2",
        "instructions": (
            "मुख्य INSIGHT #2। दूसरे बड़े विचार पर गहराई से बात करो, एक relatable "
            "example के साथ। यह insight 1 से अलग और distinct feel होना चाहिए।"
        ),
        "target_words": 420,
    },
    {
        "name": "insight_3",
        "instructions": (
            "मुख्य INSIGHT #3। तीसरे बड़े विचार पर गहराई से बात करो, एक relatable "
            "example के साथ। यह insight 1 और 2 दोनों से अलग और distinct feel होना चाहिए।"
        ),
        "target_words": 420,
    },
    {
        "name": "transformation",
        "instructions": (
            "रूपांतरण संदेश। सभी insights को जोड़ो, और बताओ कि श्रोता के लिए कौन सा "
            "बदलाव possible है।"
        ),
        "target_words": 320,
    },
    {
        "name": "cta",
        "instructions": (
            "CALL TO ACTION। मज़बूत closing, action के लिए motivate करो, "
            "subscribe/like का natural (robotic नहीं) तरीके से ज़िक्र करो।"
        ),
        "target_words": 220,
    },
]

BASE_SYSTEM_PROMPT = f"""आप "{CHANNEL_NAME}" के लिए एक master narrator हैं।
यह 2 मिलियन subscribers का YouTube channel है।

भाषा नियम:
✅ मुख्य भाषा: Devanagari (proper Hindi)
✅ Technical terms: English रखो (Transform, Breakthrough, Discipline)
✅ Author names: Original रखो (Viktor Frankl, James Clear)
✅ Book names: Original रखो (Atomic Habits, Deep Work)
✅ Concepts: Hindi में समझाओ, फिर English term दो
✅ Hindi/English का mix बिल्कुल natural रहने दो — कोई fixed ratio फॉलो मत करो,
   जो भी sentence में स्वाभाविक लगे वही रखो

English words की spelling (बहुत ज़रूरी):
- English/technical words हमेशा उनकी STANDARD, DICTIONARY-CORRECT spelling में
  लिखो (जैसे "Transform", "Breakthrough", "Discipline", "Mindset")
- कभी भी phonetic, slang, या casual spelling मत use करो
  (गलत: "Transfrom", "Bricthru", "Mindsett" — सही: "Transform", "Breakthrough")
- Author names और book titles भी उनकी original/official spelling में ही लिखो

Pause indicators (emotion is in voice settings, not tags):
- ... = चिंतन के लिए pause (reflection)
- — = नाटकीय pause (dramatic moment)
- ! = शक्तिशाली बिंदु (powerful point)
- हर sentence का अंत उचित विराम चिन्ह से करो: Hindi वाक्यों के लिए "।" और
  English/Hinglish वाक्यों के लिए "." — दोनों को सही जगह इस्तेमाल करो

Voice सेटिंग्स (emotion के लिए):
- Depth: गहरा, गंभीर
- Power: शक्तिशाली, प्रेरणादायक
- Calm: मापा हुआ, विचारशील
- Age: 55+ साल का दार्शनिक

महत्वपूर्ण:
- NO emotion tags like [serious], [pause]
- Smart pauses only (... and —)
- Professional broadcast quality, 2M subscriber channel level
- आप एक लंबी, continuous script का सिर्फ ONE SECTION लिख रहे हैं। अगर यह
  opening section नहीं है, तो दोबारा greeting/channel-intro मत दोहराओ —
  पिछले section के जहां से रुका था वहीं से स्वाभाविक रूप से आगे बढ़ो
  (context नीचे दिया जाएगा)।"""


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

    NOTE: Book selection happens ONLY in scripts/select_book.py, which runs
    as its own step earlier in the GitHub Actions workflow. This function
    just reads that result - it does NOT select a book itself, to avoid the
    double-selection bug (two books getting marked "used" in one run).
    """

    print("\n📚 Loading selected book (chosen by select_book.py)...")

    with open(SELECTED_BOOK_FILE, "r", encoding="utf-8") as f:
        selected_book = json.load(f)

    print(f"  ✅ Loaded: {selected_book.get('title')}")
    print(f"  Author: {selected_book.get('author')}")

    return selected_book


def ensure_starting_pause(script_text):
    """
    Guarantee the FULL script begins with '...' regardless of what Claude
    wrote, so the TTS engine gets a tiny lead-in and the first real word is
    pronounced correctly.
    """
    stripped = script_text.lstrip()
    if stripped.startswith("..."):
        return stripped
    return "... " + stripped


def generate_section(section, book_data, previous_ending):
    """Generate ONE section of the Devanagari script, with continuity context."""

    continuity_note = ""
    if previous_ending:
        continuity_note = f"""
Script अभी तक यहाँ तक पहुँची है (यहीं से आगे बढ़ो, इसे दोहराओ मत, और
greeting से दोबारा शुरू मत करो):
---
...{previous_ending}
---
"""
    else:
        continuity_note = f"""
यह script का सबसे पहला section है। सबसे पहला शब्द लिखने से पहले "..."
ज़रूर लगाओ, और शुरुआत में ही "{CHANNEL_NAME}" चैनल का गर्मजोशी से स्वागत
करते हुए ज़िक्र करो।
"""

    user_prompt = f"""इस किताब के लिए Devanagari (Hindi) script का
"{section['name'].upper()}" section लिखो:

Book: {book_data.get('title', 'Unknown')}
Author: {book_data.get('author', 'Unknown')}
Theme: {book_data.get('theme', '')}
Keywords: {', '.join(book_data.get('keywords', []))}

Section brief: {section['instructions']}
Target length: लगभग {section['target_words']} शब्द।
{continuity_note}
याद रखो: मुख्य भाषा Devanagari Hindi + natural English mix + सही विराम
चिन्ह ("।" Hindi वाक्यों के लिए, "." English/Hinglish के लिए)।
सिर्फ इस section का text लिखो - कोई header, कोई label, कोई meta commentary नहीं।"""

    print(f"\n✍️  Generating section: {section['name']} (~{section['target_words']} words)...")

    # Devanagari uses noticeably more tokens per word than Roman script, so
    # budget generously - this is the key fix for scripts cutting off early.
    max_tok = int(section['target_words'] * 4.5) + 300

    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        messages=[{"role": "user", "content": user_prompt}],
        system=BASE_SYSTEM_PROMPT,
    )

    return extract_text(message)


def generate_hindi_devanagari_script(book_data):
    """
    Generate the FULL Devanagari script, section by section, carrying
    context forward so the ~2200-2600 word script stays consistent in
    tone/flow across a 12-15 minute voice track.
    """

    full_script_parts = []
    previous_ending = ""

    for section in SECTIONS:
        section_text = generate_section(section, book_data, previous_ending)
        full_script_parts.append(section_text)

        # carry forward last ~400 chars as continuity context for next section
        previous_ending = section_text[-400:]

    script_text = "\n\n".join(full_script_parts)
    script_text = ensure_starting_pause(script_text)
    return script_text


def verify_hindi_quality(script_text):
    """VERIFICATION 1: Check Hindi script quality"""

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
        messages=[{"role": "user", "content": verify_prompt}],
    )

    verification_result = extract_text(response)
    print(f"  Result: {verification_result[:300]}...")

    return script_text


def verify_emotional_depth(script_text):
    """VERIFICATION 2: Check emotional depth and engagement"""

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
        messages=[{"role": "user", "content": verify_prompt}],
    )

    verification_result = extract_text(response)
    print(f"  Result: {verification_result[:300]}...")

    return script_text


def verify_word_count(script_text, target_min=2000, target_max=2800):
    """VERIFICATION 3: Word count (raised range for 12-15 min, section-based total)"""

    print("\n🔍 Verification 3: Word Count & Length")

    word_count = len(script_text.split())

    print(f"  Words: {word_count} (target: {target_min}-{target_max})")

    if target_min <= word_count <= target_max:
        print(f"  ✅ Perfect for a 12-15 min voice track!")
    elif word_count < target_min:
        print(f"  ⚠️  Slightly short ({target_min - word_count} words needed)")
    else:
        print(f"  ⚠️  Slightly long ({word_count - target_max} words over)")

    return script_text


def verify_pause_flow(script_text):
    """VERIFICATION 4: Smart pause usage"""

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


def verify_channel_mention(script_text):
    """VERIFICATION 5: Channel name mentioned near the start"""

    print("\n🔍 Verification 5: Channel Name Mention")

    opening = script_text[:600]
    mentioned = CHANNEL_NAME.lower() in opening.lower()

    print(f"  '{CHANNEL_NAME}' mentioned in opening: {'✅' if mentioned else '❌'}")

    return script_text


def main():
    """Main flow."""

    print("\n" + "=" * 70)
    print("GROW WITH BOOKS - DEVANAGARI SCRIPT (CHUNKED, VERIFIED)")
    print("=" * 70)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")

    # Load the book select_book.py already chose (no re-selecting here)
    book_data = load_selected_book()

    # Generate script - section by section
    print("\n✍️ Generating Devanagari script (section-by-section)...")
    script_text = generate_hindi_devanagari_script(book_data)

    # Verifications
    print("\n" + "=" * 70)
    print("QUALITY VERIFICATIONS (5 checks)")
    print("=" * 70)

    script_text = verify_hindi_quality(script_text)
    script_text = verify_emotional_depth(script_text)
    script_text = verify_word_count(script_text)
    script_text = verify_pause_flow(script_text)
    script_text = verify_channel_mention(script_text)

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
    print(f"\n🎉 SUCCESS! Full-length Devanagari script ready!\n")


if __name__ == "__main__":
    main()
