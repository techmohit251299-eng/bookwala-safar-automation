"""
Step 3: Generate the narration voiceover with ElevenLabs.

Reads data/script.json (written by generate_script.py) and sends the
script text — including the inline emotion tags like [serious],
[pause], [inspiring] — to ElevenLabs' v3 model, which natively
interprets those tags for delivery/emotion.

ElevenLabs caps a single request at 5000 characters. Long scripts are
split into smaller chunks (short takes reduce eleven_v3 instability)
at sentence boundaries, each chunk is converted separately using the
same seed for better cross-chunk consistency, and the resulting audio
pieces are concatenated into one final file.

Output: output/voice.mp3

Env vars:
  ELEVENLABS_API_KEY   required — script fails clearly if not set
  ELEVEN_VOICE_ID       optional override (default below is a general-purpose
                         multilingual voice — browse the ElevenLabs voice
                         library and swap in a Hindi/Hinglish-friendly one
                         you like, then set this secret)
"""

import os
from pathlib import Path
import json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCRIPT_FILE = DATA_DIR / "script.json"
VOICE_OUTPUT = OUTPUT_DIR / "voice.mp3"

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # placeholder — swap for your pick from ElevenLabs' voice library
MAX_TEST_CHARS = 900  # safety cap (~120-150 words) so testing never burns credits on a long script by mistake
MAX_CHUNK_CHARS = 1800  # short takes reduce eleven_v3 instability/drift vs longer chunks
VOICE_SEED = 42  # fixed seed across all chunks — best-effort consistency, not guaranteed


def load_script():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_text(text, max_chars=MAX_CHUNK_CHARS):
    """
    Split script text into chunks under ElevenLabs' character limit,
    breaking at sentence boundaries so emotion tags stay attached to
    the sentence they modify and never get cut mid-tag.
    """
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""

    for i, sentence in enumerate(sentences):
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


def generate_with_elevenlabs(script_text, voice_id):
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    from pydub import AudioSegment
    import io

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    chunks = chunk_text(script_text)

    print(f"Script is {len(script_text)} chars — split into {len(chunks)} chunk(s) for ElevenLabs.")

    combined = AudioSegment.empty()

    for idx, chunk in enumerate(chunks, start=1):
        print(f"  Generating chunk {idx}/{len(chunks)} ({len(chunk)} chars)...")
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=chunk,
            model_id="eleven_v3",
            seed=VOICE_SEED,
            voice_settings=VoiceSettings(
                stability=0.60,
                similarity_boost=0.85,
                style=0.35,
                use_speaker_boost=False,
            ),
        )

        audio_bytes = b"".join(audio_stream)
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        combined += segment

        # small natural pause between chunks so the stitch isn't abrupt
        combined += AudioSegment.silent(duration=300)

    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")


def main():
    data = load_script()
    script_text = data["script"]
    voice_id = os.environ.get("ELEVEN_VOICE_ID", DEFAULT_VOICE_ID)

    if data.get("mode") == "test" and len(script_text) > MAX_TEST_CHARS:
        print(
            f"[safety cap] test-mode script is {len(script_text)} chars, "
            f"trimming to {MAX_TEST_CHARS} to avoid burning credits."
        )
        script_text = script_text[:MAX_TEST_CHARS]

    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise RuntimeError(
            "ELEVENLABS_API_KEY is not set — cannot generate voice. "
            "Set the secret and re-run."
        )

    generate_with_elevenlabs(script_text, voice_id)
    print(f"Voice generated: {VOICE_OUTPUT}")


if __name__ == "__main__":
    main()
