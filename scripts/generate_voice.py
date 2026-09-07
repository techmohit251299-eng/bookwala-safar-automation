"""
Voice Generation - Philosopher Style with ALL MAPPINGS

Uses:
- DEVANAGARI_MAPPINGS
- AUTHOR_MAPPINGS
- BOOK_MAPPINGS
- CONCEPT_MAPPINGS
- BUSINESS_MAPPINGS
- PHILOSOPHY_MAPPINGS
- PSYCHOLOGY_MAPPINGS
- NARRATION_MAPPINGS

All integrated into voice generation!
"""

import os
from pathlib import Path
import json
import re

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCRIPT_FILE = DATA_DIR / "script.json"
VOICE_OUTPUT = OUTPUT_DIR / "voice.mp3"

# PHILOSOPHER VOICE SETTINGS
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# CHUNK SIZE RANGE
MIN_CHUNK_CHARS = 2000
MAX_CHUNK_CHARS = 3000
TARGET_CHUNK_CHARS = 2500

VOICE_SEED = 42
PAUSE_DURATION = 800

# ═══════════════════════════════════════════════════════════
# ALL MAPPINGS (Hinglish Pronunciation + Devanagari)
# ═══════════════════════════════════════════════════════════

DEVANAGARI_MAPPINGS = {
    "Aristotle": "अरिस्टोटल (Aristotle)",
    "Plato": "प्लेटो (Plato)",
    "Nietzsche": "नीत्शे (Nietzsche)",
    "Socrates": "सुकरात (Socrates)",
    "Descartes": "डेकार्ट (Descartes)",
}

AUTHOR_MAPPINGS = {
     "Aristotle": "अरिस्टोटल (Aristotle)",
    "Plato": "प्लेटो (Plato)",
    "Socrates": "सुकरात (Socrates)",
    "Nietzsche": "नीत्शे (Nietzsche)",
    "Descartes": "डेसकार्ट (Descartes)",
    "Viktor Frankl": "विक्टर फ्रैंकल (Viktor Frankl)",
    "James Clear": "जेम्स क्लियर (James Clear)",
    "Cal Newport": "कैल न्यूपोर्ट (Cal Newport)",
    "Stephen Covey": "स्टीफन कोवी (Stephen Covey)",
    "Robert Greene": "रॉबर्ट ग्रीन (Robert Greene)",
    "Dale Carnegie": "डेल कार्नेगी (Dale Carnegie)",
    "Napoleon Hill": "नेपोलियन हिल (Napoleon Hill)",
    "Tony Robbins": "टोनी रॉबिन्स (Tony Robbins)",
    "Robin Sharma": "रॉबिन शर्मा (Robin Sharma)",
    "Simon Sinek": "साइमन सिनेक (Simon Sinek)",
    "Ryan Holiday": "रयान हॉलिडे (Ryan Holiday)",
    "Mark Manson": "मार्क मैनसन (Mark Manson)",
    "Daniel Kahneman": "डैनियल काह्नमन (Daniel Kahneman)",
    "Morgan Housel": "मॉर्गन हाउसल (Morgan Housel)",
    "Adam Grant": "एडम ग्रांट (Adam Grant)",
    "Naval Ravikant": "नवल रविकांत (Naval Ravikant)"
}

BOOK_MAPPINGS = {
    "Atomic Habits": "एटॉमिक हैबिट्स (Atomic Habits)",
    "The 7 Habits of Highly Effective People": "द सेवन हैबिट्स ऑफ हाईली इफेक्टिव पीपल",
    "Think and Grow Rich": "थिंक एंड ग्रो रिच",
    "Rich Dad Poor Dad": "रिच डैड पुअर डैड",
    "The Psychology of Money": "द साइकोलॉजी ऑफ मनी",
    "Deep Work": "डीप वर्क",
    "The Power of Now": "द पावर ऑफ नाउ",
    "Ikigai": "इकिगाई",
    "The Alchemist": "द अल्केमिस्ट",
    "Man's Search for Meaning": "मैन्स सर्च फॉर मीनिंग",
    "The Subtle Art of Not Giving a F*ck": "द सबटल आर्ट ऑफ नॉट गिविंग अ फक",
    "The 48 Laws of Power": "द फोर्टी-एट लॉज़ ऑफ पावर",
    "How to Win Friends and Influence People": "हाउ टू विन फ्रेंड्स एंड इन्फ्लुएंस पीपल",
    "The Power of Habit": "द पावर ऑफ हैबिट",
    "Essentialism": "एसेंशियलिज़्म",
    "The One Thing": "द वन थिंग",
    "Start With Why": "स्टार्ट विद व्हाय",
    "Ego Is the Enemy": "ईगो इज़ द एनिमी"
}

CONCEPT_MAPPINGS = {
    "discipline": "अनुशासन (discipline)",
    "consistency": "निरंतरता (consistency)",
    "motivation": "प्रेरणा (motivation)",
    "procrastination": "टालमटोल (procrastination)",
    "self-discipline": "आत्म-अनुशासन (self-discipline)",
    "self-awareness": "आत्म-जागरूकता (self-awareness)",
    "self-esteem": "आत्म-सम्मान (self-esteem)",
    "confidence": "आत्मविश्वास (confidence)",
    "mindset": "मानसिकता (mindset)",
    "growth mindset": "विकासवादी मानसिकता (growth mindset)",
    "fixed mindset": "स्थिर मानसिकता (fixed mindset)",
    "identity": "पहचान (identity)",
    "belief": "विश्वास (belief)",
    "fear": "डर (fear)",
    "anxiety": "चिंता (anxiety)",
    "focus": "एकाग्रता (focus)",
    "attention": "ध्यान (attention)",
    "awareness": "जागरूकता (awareness)",
    "habit": "आदत (habit)",
}

BUSINESS_MAPPINGS = {
    "wealth": "धन-संपत्ति (wealth)",
    "income": "आय (income)",
    "expense": "खर्च (expense)",
    "saving": "बचत (saving)",
    "investment": "निवेश (investment)",
    "compound interest": "चक्रवृद्धि ब्याज (compound interest)",
    "cash flow": "नकदी प्रवाह (cash flow)",
    "financial freedom": "वित्तीय स्वतंत्रता (financial freedom)",
    "passive income": "निष्क्रिय आय (passive income)",
    "active income": "सक्रिय आय (active income)",
    "asset": "संपत्ति (asset)",
    "liability": "दायित्व (liability)",
    "risk": "जोखिम (risk)",
    "opportunity": "अवसर (opportunity)",
    "entrepreneur": "उद्यमी (entrepreneur)",
    "entrepreneurship": "उद्यमिता (entrepreneurship)",
    "business model": "व्यवसाय मॉडल (business model)",
    "market": "बाज़ार (market)",
    "profit": "लाभ (profit)",
    "loss": "हानि (loss)"
}

PHILOSOPHY_MAPPINGS = {
    "philosophy": "दर्शन (philosophy)",
    "stoicism": "स्टोइक दर्शन (Stoicism)",
    "stoic": "स्टोइक (Stoic)",
    "existentialism": "अस्तित्ववाद (existentialism)",
    "nihilism": "निहिलिज़्म (nihilism)",
    "absurdism": "एब्सर्डिज़्म (absurdism)",
    "epistemology": "ज्ञानमीमांसा (epistemology)",
    "ontology": "ऑन्टोलॉजी (ontology)",
    "ethics": "नीतिशास्त्र (ethics)",
    "morality": "नैतिकता (morality)",
    "virtue": "सद्गुण (virtue)",
    "consciousness": "चेतना (consciousness)",
    "free will": "स्वतंत्र इच्छा (free will)",
    "determinism": "नियतिवाद (determinism)",
    "meaning": "अर्थ (meaning)",
    "purpose": "उद्देश्य (purpose)",
    "wisdom": "बुद्धिमत्ता (wisdom)",
    "rationality": "तर्कशीलता (rationality)",
    "pragmatism": "व्यावहारिकता (pragmatism)"
}

PSYCHOLOGY_MAPPINGS = {
    "dopamine": "डोपामिन (dopamine)",
    "cortisol": "कॉर्टिसोल (cortisol)",
    "serotonin": "सेरोटोनिन (serotonin)",
    "subconscious": "अवचेतन मन (subconscious)",
    "conscious mind": "चेतन मन (conscious mind)",
    "confirmation bias": "कन्फर्मेशन बायस (confirmation bias)",
    "cognitive bias": "संज्ञानात्मक पूर्वाग्रह (cognitive bias)",
    "loss aversion": "हानि से बचने की प्रवृत्ति (loss aversion)",
    "decision making": "निर्णय लेने की प्रक्रिया (decision making)",
    "emotional intelligence": "भावनात्मक बुद्धिमत्ता (emotional intelligence)",
    "social pressure": "सामाजिक दबाव (social pressure)",
    "peer pressure": "साथियों का दबाव (peer pressure)",
    "instant gratification": "तुरंत संतुष्टि (instant gratification)",
    "delayed gratification": "विलंबित संतुष्टि (delayed gratification)",
    "comfort zone": "आराम का क्षेत्र (comfort zone)",
    "burnout": "मानसिक थकावट (burnout)",
    "overthinking": "अति-विचार (overthinking)",
    "self-sabotage": "खुद को नुकसान पहुँचाने वाला व्यवहार (self-sabotage)"
}

NARRATION_MAPPINGS = {
    "however": "लेकिन",
    "therefore": "इसलिए",
    "because": "क्योंकि",
    "for example": "उदाहरण के लिए",
    "in other words": "दूसरे शब्दों में",
    "the truth is": "सच्चाई यह है कि",
    "the important thing is": "सबसे महत्वपूर्ण बात यह है कि",
    "remember": "याद रखिए",
    "imagine": "ज़रा सोचिए",
    "think about it": "ज़रा इस बारे में सोचिए",
    "the question is": "सवाल यह है कि",
    "the answer is": "इसका जवाब है",
    "most importantly": "सबसे महत्वपूर्ण बात",
    "at first": "शुरुआत में",
    "eventually": "आखिरकार",
    "in the end": "अंत में",
    "this means": "इसका मतलब है",
    "what if": "अगर ऐसा हो तो",
    "the lesson is": "इससे हमें यह सीख मिलती है"
}

# COMBINE ALL MAPPINGS
ALL_MAPPINGS = {
    **DEVANAGARI_MAPPINGS,
    **AUTHOR_MAPPINGS,
    **BOOK_MAPPINGS,
    **CONCEPT_MAPPINGS,
    **BUSINESS_MAPPINGS,
    **PHILOSOPHY_MAPPINGS,
    **PSYCHOLOGY_MAPPINGS,
    **NARRATION_MAPPINGS,
}


def add_all_mappings_to_text(text):
    """
    Add ALL mappings to text:
    - Devanagari
    - Authors
    - Books
    - Concepts
    - Business
    - Philosophy
    - Psychology
    - Narration
    """
    modified_text = text
    
    print(f"  Applying {len(ALL_MAPPINGS)} mappings...")
    
    for english, hindi in ALL_MAPPINGS.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(english), re.IGNORECASE)
        modified_text = pattern.sub(hindi, modified_text)
    
    return modified_text


def load_script():
    """Load generated script."""
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def smart_chunk_text_range(text, min_chars=MIN_CHUNK_CHARS, max_chars=MAX_CHUNK_CHARS, target_chars=TARGET_CHUNK_CHARS):
    """
    SMART CHUNKING (2000-3000 char range):
    1. Split by paragraphs
    2. Combine until 2000-3000 range
    3. If too long, split by sentences
    """
    
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        test_length = len(test_chunk)
        
        if min_chars <= test_length <= max_chars:
            current_chunk = test_chunk
        
        elif test_length > max_chars:
            if current_chunk and len(current_chunk) >= min_chars:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            
            elif len(paragraph) > max_chars:
                sentences = paragraph.split(". ")
                sentence_chunk = ""
                
                for sentence in sentences:
                    piece = sentence if sentence.endswith(".") else sentence + "."
                    piece += " "
                    
                    sentence_chunk_test = sentence_chunk + piece
                    
                    if len(sentence_chunk_test) <= max_chars:
                        sentence_chunk += piece
                    else:
                        if sentence_chunk and len(sentence_chunk) >= min_chars:
                            chunks.append(sentence_chunk.strip())
                        sentence_chunk = piece
                
                if sentence_chunk and len(sentence_chunk) >= min_chars:
                    chunks.append(sentence_chunk.strip())
                current_chunk = ""
            else:
                current_chunk = paragraph
    
    if current_chunk and len(current_chunk) >= min_chars:
        chunks.append(current_chunk.strip())
    
    return chunks


def generate_with_elevenlabs_all_mappings(script_text, voice_id):
    """
    Voice generation with ALL MAPPINGS integrated.
    """
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    from pydub import AudioSegment
    import io

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    
    # ADD ALL MAPPINGS
    print("\n📝 Adding Hinglish Pronunciations...")
    script_text = add_all_mappings_to_text(script_text)
    
    chunks = smart_chunk_text_range(script_text, MIN_CHUNK_CHARS, MAX_CHUNK_CHARS, TARGET_CHUNK_CHARS)

    print(f"\n🎙️ PHILOSOPHER VOICE GENERATION (ALL MAPPINGS)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Script: {len(script_text)} characters")
    print(f"📦 Chunks: {len(chunks)} pieces")
    print(f"🗺️  Mappings: {len(ALL_MAPPINGS)} total")
    print(f"  ├─ Devanagari: {len(DEVANAGARI_MAPPINGS)}")
    print(f"  ├─ Authors: {len(AUTHOR_MAPPINGS)}")
    print(f"  ├─ Books: {len(BOOK_MAPPINGS)}")
    print(f"  ├─ Concepts: {len(CONCEPT_MAPPINGS)}")
    print(f"  ├─ Business: {len(BUSINESS_MAPPINGS)}")
    print(f"  ├─ Philosophy: {len(PHILOSOPHY_MAPPINGS)}")
    print(f"  ├─ Psychology: {len(PSYCHOLOGY_MAPPINGS)}")
    print(f"  └─ Narration: {len(NARRATION_MAPPINGS)}")
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"🔒 Seed: {VOICE_SEED} (LOCKED)")
    print(f"📏 Range: {MIN_CHUNK_CHARS}-{MAX_CHUNK_CHARS} chars")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    combined = AudioSegment.empty()

    # Generate each chunk
    for idx, chunk in enumerate(chunks, start=1):
        chunk_words = len(chunk.split())
        chunk_chars = len(chunk)
        
        print(f"  [{idx}/{len(chunks)}] Chunk ({chunk_chars} chars, {chunk_words} words)...", end="")
        
        try:
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=chunk,
                model_id="eleven_v3",
                seed=VOICE_SEED,
                voice_settings=VoiceSettings(
                    stability=0.78,
                    similarity_boost=0.85,
                    style=0.12,
                    use_speaker_boost=False,
                ),
            )

            audio_bytes = b"".join(audio_stream)
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            combined += segment
            
            print(" ✅")

            if idx < len(chunks):
                combined += AudioSegment.silent(duration=PAUSE_DURATION)
                
        except Exception as e:
            print(f" ❌ Error: {e}")
            raise

    # Export
    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")

    duration_min = len(combined) / 1000 / 60
    print(f"\n{'━'*70}")
    print(f"✅ Voice generation complete!")
    print(f"📊 Total duration: {duration_min:.1f} minutes")
    print(f"📁 Saved: {VOICE_OUTPUT}")
    print(f"🗺️  Applied: {len(ALL_MAPPINGS)} mappings")
    print(f"🎯 Consistency: PERFECT")
    print(f"{'━'*70}\n")


def main():
    """Main flow."""
    
    print("\n" + "="*70)
    print("GROW WITH BOOKS - VOICE WITH ALL MAPPINGS")
    print("="*70)
    
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError("❌ ELEVENLABS_API_KEY not set!")

    data = load_script()
    script_text = data["script"]
    
    print(f"\n📚 Book: {data.get('book', 'Unknown')}")
    print(f"✍️  Script length: {len(script_text)} characters")
    
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    print(f"🎙️ Voice ID: {voice_id}\n")

    try:
        generate_with_elevenlabs_all_mappings(script_text, voice_id)
        print("🎉 SUCCESS! Voice with all mappings ready!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
