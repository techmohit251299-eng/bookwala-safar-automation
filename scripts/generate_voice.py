"""
Step 3: Generate the narration voiceover with ElevenLabs.

Reads data/script.json (written by generate_script.py) and sends the
script text — including the inline emotion tags like [serious],
[pause], [inspiring] — to ElevenLabs' v3 model, which natively
interprets those tags for delivery/emotion.

ElevenLabs caps a single request at 5000 characters, so long scripts
(~2400 words / ~13000-15000 chars in Hinglish) are split into chunks
at sentence boundaries, each chunk is converted separately, and the
resulting audio pieces are concatenated into one final file.

Output: output/voice.mp3

Env vars:
  ELEVENLABS_API_KEY   required for a real call
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
MAX_CHUNK_CHARS = 4500  # stay safely under ElevenLabs' 5000-char hard limit


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
            model_id="eleven_v3",  # natively reads inline emotion tags
            voice_settings=VoiceSettings(
                stability=0.65,       # higher = more controlled/consistent, less erratic — professor, not storyteller
                similarity_boost=0.8, # stay close to the original voice character
                style=0.25,           # low = composed delivery, not theatrical/exaggerated
                use_speaker_boost=True,
            ),
        )
        audio_bytes = b"".join(audio_stream)
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        combined += segment

        # small natural pause between chunks so the stitch isn't abrupt
        combined += AudioSegment.silent(duration=300)

    OUTPUT_DIR.mkdir(exist_ok=True)
    combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")


def generate_fallback_demo(script_text):
    """
    Offline placeholder (silent audio) so the pipeline can be test-run
    without an ELEVENLABS_API_KEY or network access. Replace with the
    real call by setting the ELEVENLABS_API_KEY secret in CI.
    """
    import wave

    OUTPUT_DIR.mkdir(exist_ok=True)
    # rough estimate: ~150 words/min -> ~0.4s per word, for a silent placeholder
    word_count = len(script_text.split())
    duration_seconds = max(2, round(word_count * 0.4))

    placeholder_path = OUTPUT_DIR / "voice.wav"
    with wave.open(str(placeholder_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00\x00" * 16000 * duration_seconds)

    print(f"[offline demo] wrote {duration_seconds}s silent placeholder to {placeholder_path}")


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

    if os.environ.get("ELEVENLABS_API_KEY"):
        generate_with_elevenlabs(script_text, voice_id)
        print(f"Voice generated: {VOICE_OUTPUT}")
    else:
        generate_fallback_demo(script_text)


if __name__ == "__main__":
    main()
