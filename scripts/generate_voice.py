"""
Step 3: Generate the narration voiceover with ElevenLabs.

Reads data/script.json (written by generate_script.py) and sends the
script text — including the inline emotion tags like [serious],
[pause], [inspiring] — straight to ElevenLabs' v3 model, which
natively interprets those tags for delivery/emotion. No manual
audio splitting or stitching needed.

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


def load_script():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_with_elevenlabs(script_text, voice_id):
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format="mp3_44100_128",
        text=script_text,
        model_id="eleven_v3",  # natively reads inline emotion tags
        voice_settings=VoiceSettings(
            stability=0.65,       # higher = more controlled/consistent, less erratic — professor, not storyteller
            similarity_boost=0.8, # stay close to the original voice character
            style=0.25,           # low = composed delivery, not theatrical/exaggerated
            use_speaker_boost=True,
        ),
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(VOICE_OUTPUT, "wb") as f:
        for chunk in audio:
            f.write(chunk)


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
