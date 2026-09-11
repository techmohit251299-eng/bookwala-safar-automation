"""
Script Generation - SMART HINDI/DEVANAGARI (2 CHUNKS ONLY, for full 12-15 min length)

Features:
1. Devanagari script (proper Hindi)
2. English words mixed smartly (where needed), always standard/correct spelling
3. Smart pauses (... for reflection, — for drama)
4. Emotion through content + voice settings
5. Book is LOADED from selected_book.json
6. Guaranteed "..." at the very start
7. ONLY 2 CHUNKS (Part 1 and Part 2) - each chunk gets generous token budget
8. INDIAN ACCENT + POWERFUL MOTIVATION STYLE throughout
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCRIPT_FILE = DATA_DIR / "script.json"
SELECTED_BOOK_FILE = DATA_DIR / "selected_book.json"

client = Anthropic()

MODEL = "claude-sonnet-5"

CHANNEL_NAME = "Grow with Books"

# ONLY 2 CHUNKS - each ~1300 words for total ~2600 words -> 12-15 min
SECTIONS = [
    {
        "name": "part_1_hook_insights",
        "instructions": (
            "🔥 POWERFUL OPENING - शक्तिशाली शुरुआत करो! सबसे पहले एक explosive hook "
            f'लगाओ जो लोगों को जकड़ दे। फिर "{CHANNEL_NAME}" का enthusiastic स्वागत करो। '
            "फिर इस किताब की कहानी बताओ - लेखक ने यह क्यों लिखी, यह अभी क्यों ज़रूरी है। "
            "फिर INSIGHT #1 - पहला मुख्य विचार एक relatable example के साथ explain करो। "
            "फिर INSIGHT #2 - दूसरा मुख्य विचार भी relatable example के साथ। "
            "हर insight को POWERFUL बनाओ, motivation का जलवा दिखाओ।"
        ),
        "target_words": 1300,
    },
    {
        "name": "part_2_insights_transformation_cta",
        "instructions": (
            "🚀 FINAL PUNCH - INSIGHT #3 लगाओ - तीसरा बड़ा विचार powerful example के साथ। "
            "फिर सभी insights को CONNECT करो - बताओ कि श्रोता के लिए कौन सा life transformation "
            "possible है, उसका future कैसे बदल सकता है। फिर POWERFUL CALL TO ACTION - "
            "subscribe/like को natural तरीके से motivate करो (robotic नहीं)। "
            "Last line को एक POWERFUL, INSPIRING quote या statement से बंद करो।"
        ),
        "target_words": 1300,
    },
]

BASE_SYSTEM_PROMPT = f"""आप "{CHANNEL_NAME}" के लिए एक POWERFUL MOTIVATIONAL NARRATOR हैं।
यह 2 मिलियन subscribers का YouTube channel है।

🎤 VOICE & ACCENT RULES (बहुत ज़रूरी):
✅ INDIAN ACCENT USE करो - natural, authentic Indian English/Hindi mix
✅ Intonation: उतार-चढ़ाव के साथ, energetic, passionate
✅ Delivery: Powerful, motivational, inspiring - लोगों को action लेने के लिए inspire करो
✅ Tone: एक सीनियर philosopher जो harsh reality बताता है पर प्यार से
✅ Pacing: कभी-कभी slow (important points के लिए), कभी quick (excitement के लिए)
✅ Emotion: हर word में conviction होनी चाहिए

भाषा नियम:
✅ मुख्य भाषा: Devanagari (proper Hindi)
✅ Technical terms: English रखो (Transform, Breakthrough, Discipline, Mindset)
✅ Author names: Original रखो (Viktor Frankl, James Clear)
✅ Book names: Original रखो (Atomic Habits, Deep Work)
✅ Concepts: Hindi में समझाओ, फिर English term दो
✅ Hindi/English का mix बिल्कुल natural रहने दो

English words की spelling (हमेशा CORRECT):
- Standard, dictionary-correct spelling हमेशा
- कभी phonetic, slang, या casual spelling नहीं
- (सही: "Transform", "Breakthrough", "Discipline" | गलत: "Transfrom", "Bricthru")

Pause indicators (emotion is in voice settings + content):
- ... = चिंतन, reflection
- — = नाटकीय pause, dramatic moment
- ! = शक्तिशाली बिंदु
- हर sentence का अंत सही विराम चिन्ह से: "।" (Hindi) और "." (Hinglish)

महत्वपूर्ण:
- NO emotion tags like [serious], [pause]
- Smart pauses only (... and —)
- Professional broadcast quality, 2M subscriber level
- इस section से पहले कोई context दिया जाएगा - उसी से continue करो
- अगर opening section नहीं है, तो greeting दोबारा मत करो

🔥 MOTIVATION STYLE:
- Direct, honest, no sugar-coating
- Challenge the listener - कहो क्या change करना चाहिए
- Real examples, relatable stories
- Call them to action - "तुम कर सकते हो", "यह तुम्हारा समय है"
- Inspire to take ACTION, not just listen
- Powerful closing lines जो memory में रहें"""


def extract_text(message):
    """Safely pull the text block out of a Claude response."""
    for block in message.content:
        if block.type == "text":
            return block.text.strip()
    raise ValueError("❌ No text block found in Claude's response!")


def load_selected_book():
    """Load the book that select_book.py already picked."""
    print("\n📚 Loading selected book (chosen by select_book.py)...")

    with open(SELECTED_BOOK_FILE, "r", encoding="utf-8") as f:
        selected_book = json.load(f)

    print(f"  ✅ Loaded: {selected_book.get('title')}")
    print(f"  Author: {selected_book.get('author')}")

    return selected_book


def ensure_starting_pause(script_text):
    """Guarantee the FULL script begins with '...'"""
    stripped = script_text.lstrip()
    if stripped.startswith("..."):
        return stripped
    return "... " + stripped


def generate_section(section, book_data, previous_ending):
    """Generate ONE section of the Devanagari script, with continuity context."""

    continuity_note = ""
    if previous_ending:
        continuity_note = f"""
Script अभी तक यहाँ तक पहुँची है (यहीं से आगे बढ़ो, इसे दोहराओ मत):
---
...{previous_ending}
---
"""
    else:
        continuity_note = f"""
यह script का पहला section है। सबसे पहला शब्द लिखने से पहले "..."
ज़रूर लगाओ।"""

    user_prompt = f"""इस किताब के लिए POWERFUL, MOTIVATIONAL Devanagari (Hindi) script
का "{section['name'].upper()}" section लिखो:

Book: {book_data.get('title', 'Unknown')}
Author: {book_data.get('author', 'Unknown')}
Theme: {book_data.get('theme', '')}
Keywords: {', '.join(book_data.get('keywords', []))}

Section brief: {section['instructions']}
Target length: लगभग {section['target_words']} शब्द।

{continuity_note}

याद रखो:
- POWERFUL, MOTIVATIONAL tone - लोगों को inspire करो
- INDIAN ACCENT + style
- मुख्य भाषा Devanagari Hindi + natural English mix
- सही विराम चिन्ह: "।" (Hindi) और "." (Hinglish)
- सिर्फ इस section का text - कोई header, label, meta commentary नहीं"""

    print(f"\n✍️  Generating: {section['name']} (~{section['target_words']} words)...")

    # Generous token budget for 2 chunks
    max_tok = int(section['target_words'] * 5) + 400

    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tok,
        messages=[{"role": "user", "content": user_prompt}],
        system=BASE_SYSTEM_PROMPT,
    )

    return extract_text(message)


def generate_hindi_devanagari_script(book_data):
    """Generate the FULL script in only 2 CHUNKS."""

    full_script_parts = []
    previous_ending = ""

    for section in SECTIONS:
        section_text = generate_section(section, book_data, previous_ending)
        full_script_parts.append(section_text)

        # carry forward last ~500 chars as continuity context
        previous_ending = section_text[-500:]

    script_text = "\n\n".join(full_script_parts)
    script_text = ensure_starting_pause(script_text)
    return script_text


def main():
    """Main flow."""

    print("\n" + "=" * 70)
    print("GROW WITH BOOKS - DEVANAGARI SCRIPT (2 CHUNKS)")
    print("=" * 70)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("❌ ANTHROPIC_API_KEY not set!")

    # Load the book
    book_data = load_selected_book()

    # Generate script - ONLY 2 CHUNKS
    print("\n🔥 Generating POWERFUL 12-15 min script (2 chunks only)...")
    script_text = generate_hindi_devanagari_script(book_data)

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
        "accent": "Indian English/Hindi",
        "emotion_style": "POWERFUL_MOTIVATIONAL",
        "chunks": 2,
        "expected_duration": "12-15 minutes",
    }

    DATA_DIR.mkdir(exist_ok=True)
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Saved: {SCRIPT_FILE}")
    print(f"\n🔥 SUCCESS! 2-Chunk POWERFUL Script Ready!")
    print(f"  📊 Word count: {len(script_text.split())}")
    print(f"  ⏱️  Expected duration: 12-15 minutes")
    print(f"  🎤 Style: Powerful Motivational + Indian Accent\n")


if __name__ == "__main__":
    main()
