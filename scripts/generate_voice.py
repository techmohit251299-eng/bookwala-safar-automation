"""
ULTIMATE Voice Generation - Philosopher Style with Consistency Fix

FIXES:
1. Voice Inconsistency (5-7 sec lag) → Crossfade between chunks
2. Devanagari support for tough words
3. Smooth transitions
4. Consistent voice seed across all chunks

Features:
- Crossfade (500ms) between chunks (no jarring transitions)
- Same voice seed (42) across ALL chunks
- Natural longer pauses (500ms instead of 350ms)
- Devanagari automatically inserted for difficult words
- Voice continuity maintained
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
MAX_CHUNK_CHARS = 1500  # Smaller for better context
VOICE_SEED = 42  # SAME SEED FOR ALL CHUNKS (consistency!)
CROSSFADE_DURATION = 500  # 500ms crossfade between chunks
PAUSE_DURATION = 500  # Longer pause for better flow

# DEVANAGARI MAPPINGS FOR TOUGH WORDS
DEVANAGARI_MAPPINGS = {
    # Philosophers
    "Aristotle": "अरिस्टोटल (Aristotle)",
    "Plato": "प्लेटो (Plato)",
    "Nietzsche": "नीत्शे (Nietzsche)",
    "Socrates": "सुकरात (Socrates)",
    "Descartes": "डेकार्ट (Descartes)",
    "Schopenhauer": "शोपनहॉएर (Schopenhauer)",
    "Kant": "कांट (Kant)",
    "Hegel": "हेगल (Hegel)",
    "Spinoza": "स्पिनोज़ा (Spinoza)",
    "Leibniz": "लैबनिज़ (Leibniz)",
    
    # Authors
    "Viktor Frankl": "विक्टर फ्रैंकल (Viktor Frankl)",
    "James Clear": "जेम्स क्लियर (James Clear)",
    "Carol Dweck": "कैरल ड्वेक (Carol Dweck)",
    "Stephen Covey": "स्टीफन कवी (Stephen Covey)",
    "Cal Newport": "कल न्यूपोर्ट (Cal Newport)",
    
    # Complex concepts
    "phenomenology": "फिनोमेनोलॉजी (phenomenology)",
    "ontology": "ऑन्टोलॉजी (ontology)",
    "epistemology": "एपिस्टेमोलॉजी (epistemology)",
    "dialectic": "द्वंद्वात्मक (dialectic)",
    "existentialism": "अस्तित्ववाद (existentialism)",
    "pragmatism": "व्यावहारिकता (pragmatism)",
}


def add_devanagari_to_text(text):
    """
    Add Devanagari script for tough words automatically.
    Case-insensitive matching.
    """
    modified_text = text
    
    for english, devanagari in DEVANAGARI_MAPPINGS.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(english), re.IGNORECASE)
        modified_text = pattern.sub(devanagari, modified_text)
    
    return modified_text


def load_script():
    """Load generated script."""
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_text(text, max_chars=MAX_CHUNK_CHARS):
    """
    Split script into chunks at sentence boundaries.
    Smaller chunks = better context preservation = consistent voice.
    """
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


def generate_with_elevenlabs_consistency_fix(script_text, voice_id):
    """
    Generate voice with CONSISTENCY FIX:
    
    1. Crossfade between chunks (smooth transition)
    2. Same voice seed (maintain consistency)
    3. Devanagari support (pronunciation clarity)
    4. Longer natural pauses
    5. Better chunk boundaries
    """
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    from pydub import AudioSegment
    import io

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    
    # Add Devanagari to text
    script_text = add_devanagari_to_text(script_text)
    chunks = chunk_text(script_text)

    print(f"\n🎙️ PHILOSOPHER VOICE GENERATION (CONSISTENCY OPTIMIZED)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Script: {len(script_text)} characters")
    print(f"📦 Chunks: {len(chunks)} pieces")
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"🔒 Voice Seed: {VOICE_SEED} (CONSISTENT across all chunks)")
    print(f"🔗 Crossfade: {CROSSFADE_DURATION}ms (smooth transitions)")
    print(f"⏸️  Pause: {PAUSE_DURATION}ms (natural flow)")
    print(f"🇮🇳 Devanagari: Enabled (for tough words)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    combined = AudioSegment.empty()
    audio_segments = []

    # Generate all chunks
    for idx, chunk in enumerate(chunks, start=1):
        print(f"  [{idx}/{len(chunks)}] Generating chunk ({len(chunk)} chars)...")
        
        # CONSISTENCY-OPTIMIZED VOICE SETTINGS
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=chunk,
            model_id="eleven_v3",
            seed=VOICE_SEED,  # ← SAME SEED FOR ALL (KEY!)
            voice_settings=VoiceSettings(
                stability=0.75,           # ← INCREASED (more consistent)
                similarity_boost=0.85,    # ← INCREASED (authentic voice)
                style=0.15,               # ← LOWERED (less variation)
                use_speaker_boost=False,  # Measured tone
            ),
        )

        audio_bytes = b"".join(audio_stream)
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        audio_segments.append(segment)

    # Combine with CROSSFADE (not just silence!)
    print(f"\n🔗 Combining {len(audio_segments)} chunks with crossfade...\n")
    
    for idx, segment in enumerate(audio_segments):
        if idx == 0:
            # First chunk - add as is
            combined = segment
        else:
            # Add crossfade with previous segment
            # Crossfade: last 500ms of previous + first 500ms of current
            overlap = min(CROSSFADE_DURATION, len(combined), len(segment))
            
            if overlap > 0:
                # Crossfade overlap
                crossfaded = combined[:-overlap].append(
                    combined[-overlap:].cross_fade_with(
                        segment[:overlap], 
                        duration=overlap
                    )
                ).append(segment[overlap:])
                combined = crossfaded
            else:
                # Fallback: simple concatenation with pause
                combined += segment
        
        # Add natural pause after each chunk (except last)
        if idx < len(audio_segments) - 1:
            combined += AudioSegment.silent(duration=PAUSE_DURATION)

    # Export
    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")

    duration_min = len(combined) / 1000 / 60
    print(f"✅ Voice generation complete!")
    print(f"📊 Total duration: {duration_min:.1f} minutes")
    print(f"📁 Saved: {VOICE_OUTPUT}")
    print(f"🎯 Consistency: OPTIMIZED (crossfade + fixed seed)")
    print(f"🇮🇳 Devanagari: ENABLED\n")


def main():
    """Main flow."""
    
    print("\n" + "="*60)
    print("GROW WITH BOOKS - PHILOSOPHER VOICE (CONSISTENCY FIXED)")
    print("="*60)
    
    # Check API key
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError(
            "❌ ELEVENLABS_API_KEY not set!\n"
            "Add to GitHub Secrets: Settings → Secrets → ELEVENLABS_API_KEY"
        )

    # Load script
    data = load_script()
    script_text = data["script"]
    
    print(f"\n📚 Book: {data.get('book', 'Unknown')}")
    print(f"✍️  Script length: {len(script_text)} characters (~{len(script_text.split())} words)")
    
    # Get voice ID
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"🎯 Style: Philosopher (Calm, Wise, Consistent)")
    print(f"🔧 Optimization: Crossfade + Fixed Seed + Devanagari\n")

    # Generate voice
    try:
        generate_with_elevenlabs_consistency_fix(script_text, voice_id)
        print("🎉 SUCCESS! Consistent philosopher voice ready!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
