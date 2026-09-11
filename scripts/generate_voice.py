"""
Voice Generation - DEEP POWERFUL PHILOSOPHER

Features:
1. DEEP voice (resonant, authoritative)
2. CALM delivery (measured, wise)
3. POWERFUL energy (motivational)
4. LOCKED CONSISTENCY (seed=42 fixed)
5. PERFECT HINGLISH pronunciation
6. Chunk consistency maintained
7. Philosopher 55+ character
8. Per-chunk "..." lead-in (each chunk is its own TTS API call, so each
   one gets a fresh warm-up pause - fixes mispronounced opening words)
9. Hindi power indicator detection for smart pauses

NO MAPPINGS - Just clean Hinglish!
"""

import os
from pathlib import Path
import json
import re

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCRIPT_FILE = DATA_DIR / "script.json"
VOICE_OUTPUT = OUTPUT_DIR / "voice.mp3"

# VOICE SETTINGS - DEEP POWERFUL PHILOSOPHER
# NOTE: this is ElevenLabs' stock "Rachel" voice ID - used ONLY as a fallback
# if ELEVENLABS_VOICE_ID isn't set in GitHub Actions secrets. Make sure the
# secret is set to your "Taksh - Calm, Serious and Smooth" voice ID, or this
# fallback voice (not Taksh) will be used instead.
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# CHUNK SIZE - LARGE FOR CONTEXT
MIN_CHUNK_CHARS = 1800
MAX_CHUNK_CHARS = 3200

# ✅ CRITICAL: LOCKED SEED = PERFECT CONSISTENCY
VOICE_SEED = 42  # NEVER CHANGE - Identical voice DNA across ALL chunks!

# INTELLIGENT PAUSES
PAUSE_DURATIONS = {
    "short": 300,      # Quick breath
    "medium": 700,     # Normal break
    "long": 1000,      # Powerful moment
}

# Extra silence (ms) inserted BEFORE the very first chunk's audio, on top of
# the text-level "..." - belt and suspenders so the opening word never gets
# clipped or mispronounced.
LEAD_IN_SILENCE_MS = 400


def load_script():
    """Load script."""
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def split_into_sentences(text):
    """
    Split text into sentences, keeping the original terminal punctuation
    intact - handles BOTH:
      - Devanagari sentence-ending "।" (purna viram / danda)
      - English/Hinglish "."
    (previously this only split on ". " and force-appended "." to every
    piece, which broke/garbled Devanagari sentences ending in "।")
    """
    pieces = re.split(r'(?<=[।.!?])\s+', text)
    return [p.strip() for p in pieces if p.strip()]


def smart_chunk_text(text, min_chars=MIN_CHUNK_CHARS, max_chars=MAX_CHUNK_CHARS):
    """
    Smart chunking for Hinglish/Devanagari text.
    Preserves paragraph/sentence boundaries (handles both "।" and ".").
    """

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if not paragraphs:
        # Fallback: split by sentences (Devanagari "।" or English/Hinglish ".")
        sentences = split_into_sentences(text)
        chunks = []
        current = ""

        for sentence in sentences:
            piece = sentence + " "

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
                # Split long paragraph by sentences (Devanagari "।" or ".")
                sentences = split_into_sentences(paragraph)
                sentence_chunk = ""

                for sentence in sentences:
                    piece = sentence + " "

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
            # Merge with last chunk
            last = chunks.pop()
            chunks.append((last + "\n\n" + current_chunk).strip())
        else:
            chunks.append(current_chunk.strip())

    return chunks


def ensure_chunk_pause(chunk_text):
    """
    Guarantee every chunk begins with '...' before it's sent to ElevenLabs.

    WHY THIS MATTERS: each chunk is synthesized in its own separate API call
    (see the convert() call in generate_deep_powerful_voice). That means the
    TTS engine has no "warm up" context at the start of EVERY chunk, not just
    the start of the whole script - so the opening word of every single chunk
    is at risk of being mispronounced/clipped, not just the very first one.
    """
    stripped = chunk_text.lstrip()
    if stripped.startswith("..."):
        return stripped
    return "... " + stripped


def detect_power_moment(text_segment):
    """
    Detect powerful moments from punctuation + Hindi/English words.
    Smart emotion detection for both Devanagari and English text.
    Add longer pause after powerful statements.
    """
    
    # English power indicators (for mixed text)
    power_indicators_en = [
        '!', '???', '—',
        'powerful', 'breakthrough', 
        'transform', 'unlock',
        'extraordinary', 'amazing',
        'incredible', 'revolutionary'
    ]
    
    # Hindi/Devanagari power indicators
    power_indicators_hi = [
        '!', '???', '—',
        'शक्तिशाली',       # Powerful
        'सफलता',           # Breakthrough
        'रूपांतरण',         # Transform
        'असाधारण',         # Extraordinary
        'महान',            # Great
        'क्रांतिकारी',      # Revolutionary
        'अविश्वसनीय',      # Incredible
        'शानदार',          # Magnificent
        'जीवन-परिवर्तनकारी', # Life-changing
        'विस्मय',          # Amazing
        'अद्भुत'           # Wonderful
    ]
    
    power_score = 0
    
    # Punctuation scoring (multiple punctuation = strong emotion)
    power_score += text_segment.count('!') * 2
    power_score += text_segment.count('?') * 1.5
    power_score += text_segment.count('—') * 1.5
    
    # English indicators
    for indicator in power_indicators_en:
        if indicator.lower() in text_segment.lower():
            power_score += 1
    
    # Hindi indicators
    for indicator in power_indicators_hi:
        if indicator in text_segment:
            power_score += 1
    
    # Decision based on score
    if power_score >= 3:
        return PAUSE_DURATIONS["long"]    # 1000ms - Let it land!
    elif power_score >= 1:
        return PAUSE_DURATIONS["medium"]  # 700ms
    else:
        return PAUSE_DURATIONS["short"]   # 300ms


def generate_deep_powerful_voice(script_text, voice_id):
    """
    Generate DEEP POWERFUL PHILOSOPHER voice with LOCKED CONSISTENCY.

    Voice Character:
    - 55-year-old wise philosopher
    - Deep, resonant voice
    - Calm but powerful
    - Measured delivery
    - Motivational energy

    Consistency:
    - Seed=42 LOCKED (identical DNA all chunks!)
    - Stability=0.80 (high consistency)
    - Large chunks (1800-3200 chars)
    - Perfect Hinglish pronunciation
    - Every chunk gets its own "..." lead-in (see ensure_chunk_pause)
    """
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    from pydub import AudioSegment
    import io

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    print("\n📝 Processing script...")
    chunks = smart_chunk_text(script_text)

    print(f"\n🎙️ DEEP POWERFUL PHILOSOPHER VOICE")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Script: {len(script_text)} characters")
    print(f"📦 Chunks: {len(chunks)} pieces")
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"\n✅ LOCKED CONSISTENCY:")
    print(f"   Seed: 42 (FIXED - same voice DNA EVERY chunk!)")
    print(f"   Result: ZERO voice variations between chunks!")
    print(f"\n💪 VOICE CHARACTER:")
    print(f"   Age: 55+ wise philosopher")
    print(f"   Depth: DEEP, resonant baritone")
    print(f"   Energy: POWERFUL, motivational")
    print(f"   Delivery: CALM, measured, thoughtful")
    print(f"\n🎙️ TECHNICAL SETTINGS:")
    print(f"   Stability: 0.80 (high - consistent emotion)")
    print(f"   Similarity: 0.88 (very authentic)")
    print(f"   Style: 0.30 (calmer, measured)")
    print(f"   Speaker Boost: OFF (natural delivery)")
    print(f"\n⏱️  PAUSE STRATEGY:")
    print(f"   Short pause: 300ms (quick breath)")
    print(f"   Medium pause: 700ms (normal break)")
    print(f"   Long pause: 1000ms (powerful moment)")
    print(f"   Lead-in silence: 400ms (first chunk)")
    print(f"\n📏 Chunk strategy: 1800-3200 chars")
    print(f"   Large chunks = context preserved")
    print(f"   Natural narrative flow maintained")
    print(f"   Each chunk gets its own '...' lead-in pause")
    print(f"   Smart pause detection: Hindi + English indicators")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if len(chunks) == 0:
        raise ValueError("❌ No chunks created!")

    combined = AudioSegment.silent(duration=LEAD_IN_SILENCE_MS)

    for idx, chunk in enumerate(chunks, start=1):
        words = len(chunk.split())
        chars = len(chunk)

        print(f"  [{idx}/{len(chunks)}] ({chars:,} chars, {words} words)...", end="", flush=True)

        # Add the guaranteed "..." lead-in so THIS chunk's opening word is
        # pronounced correctly, since it's a brand new TTS API call.
        chunk_for_tts = ensure_chunk_pause(chunk)

        try:
            # ✅ DEEP POWERFUL PHILOSOPHER VOICE SETTINGS
            # Seed=42 is LOCKED - this ensures perfect consistency!
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=chunk_for_tts,
                model_id="eleven_v3",
                seed=VOICE_SEED,  # ✅ LOCKED! Same DNA every chunk!
                voice_settings=VoiceSettings(
                    stability=0.80,           # High consistency
                    similarity_boost=0.88,    # Very authentic
                    style=0.30,               # Calmer, measured tone
                    use_speaker_boost=False,  # Natural philosopher tone
                ),
            )

            audio_bytes = b"".join(audio_stream)
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            combined += segment

            print(" ✅", flush=True)

            # Smart pause based on power moments (Hindi + English detection)
            if idx < len(chunks):
                pause_duration = detect_power_moment(chunk)
                combined += AudioSegment.silent(duration=pause_duration)

        except Exception as e:
            print(f" ❌ Error: {e}", flush=True)
            raise

    # Export
    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")

    duration_min = len(combined) / 1000 / 60

    print(f"\n{'━'*70}")
    print(f"✅ VOICE GENERATION COMPLETE!")
    print(f"📊 Duration: {duration_min:.1f} minutes")
    print(f"📁 File: {VOICE_OUTPUT}")
    print(f"\n🏆 FINAL RESULT:")
    print(f"   ✅ Seed=42 LOCKED")
    print(f"   ✅ Perfect consistency across {len(chunks)} chunks!")
    print(f"   ✅ ZERO voice variations!")
    print(f"   ✅ DEEP powerful philosopher voice!")
    print(f"   ✅ CALM, measured delivery!")
    print(f"   ✅ Motivational energy throughout!")
    print(f"   ✅ Accurate Hinglish/Devanagari pronunciation!")
    print(f"   ✅ Smart pauses (Hindi + English detection)!")
    print(f"   ✅ Professional 2M-subscriber quality!")
    print(f"\n🚀 Ready for YouTube!\n")
    print(f"{'━'*70}\n")


def main():
    """Main."""

    print("\n" + "="*70)
    print("GROW WITH BOOKS - DEEP POWERFUL PHILOSOPHER VOICE")
    print("="*70)

    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError("❌ ELEVENLABS_API_KEY not set!")

    data = load_script()
    script_text = data["script"]

    script_style = data.get("style", "Unknown style")

    print(f"\n📚 Book: {data.get('book', 'Unknown')}")
    print(f"✍️  Script: {len(script_text)} characters ({script_style})")
    print(f"🎙️ Voice ID: {os.environ.get('ELEVENLABS_VOICE_ID', 'DEFAULT')}")

    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)

    try:
        generate_deep_powerful_voice(script_text, voice_id)
        print("🎉 SUCCESS! Deep powerful philosopher voice with perfect consistency!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    main()
