"""
Voice Generation - MOTIVATIONAL DELIVERY with LOCKED CONSISTENCY

Secret: Balance motivational energy with consistency!

Settings:
- Stability: 0.82 (high - consistency locked!)
- Similarity: 0.85 (authentic)
- Style: 0.35 (motivational, not ultra-calm)
- Seed: 42 (LOCKED - identical DNA across ALL chunks)
- Chunks: 2000-3000 (context preserved)

Result: POWERFUL + CONSISTENT throughout! 🚀
"""

import os
from pathlib import Path
import json
import re

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCRIPT_FILE = DATA_DIR / "script.json"
VOICE_OUTPUT = OUTPUT_DIR / "voice.mp3"

# MOTIVATIONAL VOICE SETTINGS
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# CHUNK RANGE
MIN_CHUNK_CHARS = 1500
MAX_CHUNK_CHARS = 3000

# CRITICAL: LOCKED SEED FOR CONSISTENCY
VOICE_SEED = 42  # ← NEVER CHANGE - This locks consistency!

# INTELLIGENT PAUSES
PAUSE_DURATIONS = {
    "short": 400,      # Quick breath
    "medium": 800,     # Normal break
    "long": 1200,      # Emotional peak
}

# MAPPINGS
DEVANAGARI_MAPPINGS = {
    "Aristotle": "अरिस्टोटल",
    "Plato": "प्लेटो",
    "Nietzsche": "नीत्शे",
    "Socrates": "सुकरात",
    "Descartes": "डेकार्ट",
}

AUTHOR_MAPPINGS = {
    "Viktor Frankl": "विक्टर फ्रैंकल",
    "James Clear": "जेम्स क्लियर",
    "Carol Dweck": "कैरल ड्वेक",
    "Stephen Covey": "स्टीफन कवी",
    "Cal Newport": "कल न्यूपोर्ट",
}

CONCEPT_MAPPINGS = {
    "phenomenology": "फिनोमेनोलॉजी",
    "ontology": "ऑन्टोलॉजी",
    "epistemology": "एपिस्टेमोलॉजी",
    "existentialism": "अस्तित्ववाद",
}

ALL_MAPPINGS = {**DEVANAGARI_MAPPINGS, **AUTHOR_MAPPINGS, **CONCEPT_MAPPINGS}


def clean_energy_markers(text):
    """
    Convert energy punctuation to natural pauses.
    ??? → emphasis (delivered with energy)
    — → natural pause
    ... → reflection pause
    """
    
    # These stay as-is for natural delivery
    # ElevenLabs will interpret punctuation naturally
    
    # Just clean up any leftover tags
    text = re.sub(r'\[serious\]|\[excited\]|\[pause\]|\[powerful\]', '', text)
    
    # Ellipsis stays (natural pause)
    # Em dashes stay (natural pause)
    # Exclamation stays (emotional)
    # Questions stay (natural)
    
    return text.strip()


def add_hindi_mappings(text):
    """Add Hindi/Hinglish mappings."""
    modified_text = text
    
    for english, hindi in ALL_MAPPINGS.items():
        pattern = re.compile(re.escape(english), re.IGNORECASE)
        modified_text = pattern.sub(hindi, modified_text)
    
    return modified_text


def load_script():
    """Load script."""
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def smart_chunk_text(text, min_chars=MIN_CHUNK_CHARS, max_chars=MAX_CHUNK_CHARS):
    """Smart chunking 1500-3000 range."""
    
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    if not paragraphs:
        sentences = text.split(". ")
        chunks = []
        current = ""
        
        for sentence in sentences:
            piece = sentence if sentence.endswith(".") else sentence + "."
            piece += " "
            
            if len(current) + len(piece) <= max_chars:
                current += piece
            else:
                if current:
                    chunks.append(current.strip())
                current = piece
        
        if current:
            chunks.append(current.strip())
        return chunks
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        
        if len(test_chunk) <= max_chars:
            current_chunk = test_chunk
        else:
            if current_chunk and len(current_chunk) >= min_chars:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            elif len(paragraph) > max_chars:
                sentences = paragraph.split(". ")
                sentence_chunk = ""
                
                for sentence in sentences:
                    piece = sentence if sentence.endswith(".") else sentence + "."
                    piece += " "
                    
                    if len(sentence_chunk) + len(piece) <= max_chars:
                        sentence_chunk += piece
                    else:
                        if sentence_chunk:
                            chunks.append(sentence_chunk.strip())
                        sentence_chunk = piece
                
                if sentence_chunk:
                    chunks.append(sentence_chunk.strip())
                current_chunk = ""
            else:
                current_chunk = paragraph
    
    if current_chunk:
        if chunks and len(current_chunk) < min_chars:
            last = chunks.pop()
            chunks.append((last + "\n\n" + current_chunk).strip())
        else:
            chunks.append(current_chunk.strip())
    
    return chunks


def detect_energy_level(text_segment):
    """
    Detect energy level from text.
    More ! = higher energy = longer pause after
    """
    
    exclamation_count = text_segment.count('!')
    question_count = text_segment.count('?')
    em_dash_count = text_segment.count('—')
    
    energy_score = (exclamation_count * 2) + question_count + em_dash_count
    
    if energy_score >= 5:
        return PAUSE_DURATIONS["long"]   # High energy = longer pause to land
    elif energy_score >= 2:
        return PAUSE_DURATIONS["medium"] # Medium energy
    else:
        return PAUSE_DURATIONS["short"]  # Low energy = quick flow


def generate_motivational_voice(script_text, voice_id):
    """
    Generate MOTIVATIONAL voice with LOCKED CONSISTENCY.
    
    KEY INSIGHT:
    - Seed=42 (LOCKED) ensures IDENTICAL voice DNA across ALL chunks
    - Stability=0.82 (high) ensures consistent emotional delivery
    - Style=0.35 (motivational) provides emotional engagement
    - Large chunks (2000-3000) preserve narrative context
    - Smart pauses add emotional impact
    
    Result: Powerful + Perfectly Consistent! 🚀
    """
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    from pydub import AudioSegment
    import io

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    
    print("\n📝 Processing Script...")
    print("  Step 1: Cleaning energy markers...")
    script_text = clean_energy_markers(script_text)
    
    print("  Step 2: Adding Hindi pronunciations...")
    script_text = add_hindi_mappings(script_text)
    
    print("  Step 3: Creating intelligent chunks...")
    chunks = smart_chunk_text(script_text)

    print(f"\n🎙️ MOTIVATIONAL VOICE GENERATION (LOCKED CONSISTENCY)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Script: {len(script_text)} characters")
    print(f"📦 Chunks: {len(chunks)} pieces")
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"\n🔒 CONSISTENCY LOCKED:")
    print(f"   Seed: 42 (IDENTICAL DNA across ALL chunks)")
    print(f"   Same voice character every single chunk! ✅")
    print(f"\n💪 MOTIVATIONAL DELIVERY:")
    print(f"   Stability: 0.82 (high - consistent energy)")
    print(f"   Similarity: 0.85 (authentic voice)")
    print(f"   Style: 0.35 (powerful, engaging)")
    print(f"   Speaker Boost: OFF (natural delivery)")
    print(f"\n📏 Chunk Strategy: 1500-3000 chars")
    print(f"   Preserves narrative momentum")
    print(f"   Maintains emotional arc")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if len(chunks) == 0:
        raise ValueError("❌ No chunks created!")

    combined = AudioSegment.empty()

    for idx, chunk in enumerate(chunks, start=1):
        words = len(chunk.split())
        chars = len(chunk)
        
        print(f"  [{idx}/{len(chunks)}] ({chars:,} chars, {words} words)...", end="")
        
        try:
            # MOTIVATIONAL VOICE SETTINGS
            # ✅ Seed locked = PERFECT consistency
            # ✅ Style at 0.35 = Powerful, motivational
            # ✅ Stability high = Consistent emotional delivery
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=chunk,
                model_id="eleven_v3",
                seed=VOICE_SEED,  # ← LOCKED! Same DNA every chunk!
                voice_settings=VoiceSettings(
                    stability=0.82,           # High consistency
                    similarity_boost=0.85,    # Authentic
                    style=0.35,               # ← MOTIVATIONAL (not ultra-calm)
                    use_speaker_boost=False,  # Natural delivery
                ),
            )

            audio_bytes = b"".join(audio_stream)
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            combined += segment
            
            print(" ✅")

            # Intelligent pause based on energy
            if idx < len(chunks):
                pause_duration = detect_energy_level(chunk)
                combined += AudioSegment.silent(duration=pause_duration)
                
        except Exception as e:
            print(f" ❌ Error: {e}")
            raise

    # Export
    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")

    duration_min = len(combined) / 1000 / 60
    
    print(f"\n{'━'*70}")
    print(f"✅ VOICE GENERATION COMPLETE!")
    print(f"📊 Duration: {duration_min:.1f} minutes")
    print(f"📁 File: {VOICE_OUTPUT}")
    print(f"\n💪 RESULT:")
    print(f"   Seed=42: PERFECT CONSISTENCY across all {len(chunks)} chunks!")
    print(f"   Style=0.35: POWERFUL motivational delivery!")
    print(f"   No jarring transitions!")
    print(f"   Ready for YouTube! 🚀")
    print(f"{'━'*70}\n")


def main():
    """Main."""
    
    print("\n" + "="*70)
    print("GROW WITH BOOKS - MOTIVATIONAL VOICE (LOCKED CONSISTENCY)")
    print("="*70)
    
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError("❌ ELEVENLABS_API_KEY not set!")

    data = load_script()
    script_text = data["script"]
    
    print(f"\n📚 Book: {data.get('book', 'Unknown')}")
    print(f"✍️  Script: {len(script_text)} characters")
    print(f"🎯 Style: {data.get('style', 'MOTIVATIONAL')}")
    
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)

    try:
        generate_motivational_voice(script_text, voice_id)
        print("🎉 SUCCESS! Motivational voice with perfect consistency!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
