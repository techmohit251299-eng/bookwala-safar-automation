"""
Voice Generation - Bookwala Safar
Simple, clean, quality-focused ElevenLabs TTS.
"""

import os
import io
import re
import sys
import json
from pathlib import Path

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from pydub import AudioSegment

# ── Paths ──────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCRIPT_FILE = DATA_DIR / "script.json"
VOICE_OUTPUT = OUTPUT_DIR / "voice.mp3"

# ── Voice config ───────────────────────────────────────
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
MODEL_ID = "eleven_multilingual_v2"

# Tuned for a calm, professional instructor tone — less monotone,
# more natural pacing/expression than the old settings.
VOICE_SETTINGS = VoiceSettings(
    stability=0.5,
    similarity_boost=0.8,
    style=0.3,
    use_speaker_boost=True,
)

CHUNK_TARGET_CHARS = 2500  # ElevenLabs handles long chunks fine; smaller = more API calls
PAUSE_MS = 500  # gap between chunks — shorter = more natural flow


# ── Pronunciation fixes ────────────────────────────────
# IMPORTANT: only the Devanagari form is spoken — never "Word (English)"
# together, since that makes the voice say every name twice.
PRONUNCIATION_MAP = {
    "Aristotle": "अरिस्टोटल",
    "Plato": "प्लेटो",
    "Socrates": "सुकरात",
    "Nietzsche": "नीत्शे",
    "Descartes": "डेकार्ट",
    "Viktor Frankl": "विक्टर फ्रैंकल",
    "James Clear": "जेम्स क्लियर",
    "Cal Newport": "कैल न्यूपोर्ट",
    "Stephen Covey": "स्टीफन कोवी",
    "Robert Greene": "रॉबर्ट ग्रीन",
    "Dale Carnegie": "डेल कार्नेगी",
    "Napoleon Hill": "नेपोलियन हिल",
    "Tony Robbins": "टोनी रॉबिन्स",
    "Robin Sharma": "रॉबिन शर्मा",
    "Simon Sinek": "साइमन सिनेक",
    "Ryan Holiday": "रयान हॉलिडे",
    "Mark Manson": "मार्क मैनसन",
    "Daniel Kahneman": "डैनियल काह्नमन",
    "Morgan Housel": "मॉर्गन हाउसल",
    "Adam Grant": "एडम ग्रांट",
    "Naval Ravikant": "नवल रविकांत",
    "Atomic Habits": "एटॉमिक हैबिट्स",
    "The 7 Habits of Highly Effective People": "द सेवन हैबिट्स ऑफ हाईली इफेक्टिव पीपल",
    "Think and Grow Rich": "थिंक एंड ग्रो रिच",
    "Rich Dad Poor Dad": "रिच डैड पुअर डैड",
    "The Psychology of Money": "द साइकोलॉजी ऑफ मनी",
}


def apply_pronunciations(text: str) -> str:
    """Replace names/titles with their Devanagari form, longest match first."""
    for english, hindi in sorted(PRONUNCIATION_MAP.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(r"\b" + re.escape(english) + r"\b", hindi, text, flags=re.IGNORECASE)
    return text


def chunk_text(text: str, target_chars: int = CHUNK_TARGET_CHARS) -> list[str]:
    """Split on paragraph boundaries, never mid-sentence, close to target size."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= target_chars or not current:
            current = candidate
        else:
            chunks.append(current.strip())
            current = para

    if current:
        chunks.append(current.strip())
    return chunks


def generate_voice(script_text: str, voice_id: str) -> bool:
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    script_text = apply_pronunciations(script_text)
    chunks = chunk_text(script_text)

    print(f"🎙️  Generating {len(chunks)} chunk(s) with voice {voice_id}...")

    combined = AudioSegment.empty()
    for i, chunk in enumerate(chunks, 1):
        print(f"  [{i}/{len(chunks)}] {len(chunk)} chars...", end=" ", flush=True)
        try:
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                model_id=MODEL_ID,
                output_format="mp3_44100_128",
                text=chunk,
                voice_settings=VOICE_SETTINGS,
            )
            segment = AudioSegment.from_file(io.BytesIO(b"".join(audio_stream)), format="mp3")
            combined += segment
            if i < len(chunks):
                combined += AudioSegment.silent(duration=PAUSE_MS)
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
            return False

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")
    print(f"✅ Saved {VOICE_OUTPUT} ({len(combined) / 1000 / 60:.1f} min)")
    return True


def main():
    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("❌ ELEVENLABS_API_KEY not set")
        sys.exit(1)

    if not SCRIPT_FILE.exists():
        print(f"❌ Script file not found: {SCRIPT_FILE}")
        sys.exit(1)

    data = json.loads(SCRIPT_FILE.read_text(encoding="utf-8"))
    script_text = data.get("script", "")
    if not script_text:
        print("❌ Script is empty")
        sys.exit(1)

    print(f"📚 Book: {data.get('book', 'Unknown')} | {len(script_text)} chars")

    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    if not generate_voice(script_text, voice_id):
        sys.exit(1)


if __name__ == "__main__":
    main()
