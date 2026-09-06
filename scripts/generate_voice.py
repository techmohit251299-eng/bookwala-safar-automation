"""
FIXED Voice Generation - Philosopher Style (Working Version)

FIXES:
1. Removed buggy cross_fade_with method
2. Using simple, reliable concatenation + overlap
3. Seed=42 FIXED (consistency!)
4. Devanagari support
5. NO MORE PYDUB ERRORS!
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
MAX_CHUNK_CHARS = 1500
VOICE_SEED = 42  # SAME SEED FOR ALL CHUNKS
PAUSE_DURATION = 600  # 600ms pause between chunks (natural breathing)

# DEVANAGARI MAPPINGS
DEVANAGARI_MAPPINGS = {
    "Aristotle": "अरिस्टोटल (Aristotle)",
    "Plato": "प्लेटो (Plato)",
    "Nietzsche": "नीत्शे (Nietzsche)",
    "Socrates": "सुकरात (Socrates)",
    "Descartes": "डेकार्ट (Descartes)",
    "Viktor Frankl": "विक्टर फ्रैंकल (Viktor Frankl)",
    "James Clear": "जेम्स क्लियर (James Clear)",
    "Carol Dweck": "कैरल ड्वेक (Carol Dweck)",
    "Stephen Covey": "स्टीफन कवी (Stephen Covey)",
    "Cal Newport": "कल न्यूपोर्ट (Cal Newport)",
}


def add_devanagari_to_text(text):
    """Add Devanagari automatically."""
    modified_text = text
    for english, devanagari in DEVANAGARI_MAPPINGS.items():
        pattern = re.compile(re.escape(english), re.IGNORECASE)
        modified_text = pattern.sub(devanagari, modified_text)
    return modified_text


def load_script():
    """Load generated script."""
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_text(text, max_chars=MAX_CHUNK_CHARS):
    """Split into chunks at sentence boundaries."""
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        piece = sentence if sentence.endswith(".") else sentence + "."
        piece += " "

        if len(current) + len(piece) > max_chars and current:
            chunks.append(current.strip())
            current = piece
        else:
            current += piece

    if current.strip():
        chunks.append(current.strip())

    return chunks


def generate_with_elevenlabs_simple(script_text, voice_id):
    """
    SIMPLE, RELIABLE voice generation:
    - Generate each chunk
    - Combine with natural pauses
    - NO complex crossfading (pydub bug)
    """
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    from pydub import AudioSegment
    import io

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    
    # Add Devanagari
    script_text = add_devanagari_to_text(script_text)
    chunks = chunk_text(script_text)

    print(f"\n🎙️ PHILOSOPHER VOICE GENERATION (FIXED)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Script: {len(script_text)} characters")
    print(f"📦 Chunks: {len(chunks)} pieces")
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"🔒 Voice Seed: {VOICE_SEED} (CONSISTENT)")
    print(f"⏸️  Pause: {PAUSE_DURATION}ms (natural breathing)")
    print(f"🇮🇳 Devanagari: Enabled")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    combined = AudioSegment.empty()

    # Generate each chunk
    for idx, chunk in enumerate(chunks, start=1):
        print(f"  [{idx}/{len(chunks)}] Generating chunk ({len(chunk)} chars)...")
        
        try:
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=chunk,
                model_id="eleven_v3",
                seed=VOICE_SEED,  # SAME SEED (KEY!)
                voice_settings=VoiceSettings(
                    stability=0.75,
                    similarity_boost=0.85,
                    style=0.15,
                    use_speaker_boost=False,
                ),
            )

            audio_bytes = b"".join(audio_stream)
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            combined += segment

            # Add natural pause after chunk (except last)
            if idx < len(chunks):
                combined += AudioSegment.silent(duration=PAUSE_DURATION)
                
        except Exception as e:
            print(f"  ❌ Chunk {idx} error: {e}")
            raise

    # Export
    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")

    duration_min = len(combined) / 1000 / 60
    print(f"\n✅ Voice generation complete!")
    print(f"📊 Total duration: {duration_min:.1f} minutes")
    print(f"📁 Saved: {VOICE_OUTPUT}")
    print(f"🎯 Consistency: PERFECT (fixed seed)")
    print(f"🇮🇳 Devanagari: ENABLED\n")


def main():
    """Main flow."""
    
    print("\n" + "="*60)
    print("GROW WITH BOOKS - PHILOSOPHER VOICE (FINAL FIXED)")
    print("="*60)
    
    # Check API key
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError("❌ ELEVENLABS_API_KEY not set!")

    # Load script
    data = load_script()
    script_text = data["script"]
    
    print(f"\n📚 Book: {data.get('book', 'Unknown')}")
    print(f"✍️  Script length: {len(script_text)} characters (~{len(script_text.split())} words)")
    
    # Get voice ID
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"🎯 Style: Philosopher (Calm, Wise)\n")

    # Generate voice
    try:
        generate_with_elevenlabs_simple(script_text, voice_id)
        print("🎉 SUCCESS! Philosopher voice ready!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
