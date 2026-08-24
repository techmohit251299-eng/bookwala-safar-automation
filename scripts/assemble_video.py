"""
Step 5: Assemble the final video.

Combines:
  - output/background_loop.mp4  (hazy zooming background, from step 4)
  - output/voice.mp3 (or voice.wav fallback)  (narration, from step 3)
  - a book cover image (fetched from Google Books, free/no key — falls
    back to a generated placeholder card if unavailable)
  - burned-in captions, timed proportionally across the audio's actual
    duration (via ffprobe) from the script text (emotion tags stripped)
  - an audio waveform strip at the bottom

Output: output/final_video.mp4
"""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SELECTED_FILE = DATA_DIR / "selected_book.json"
SCRIPT_FILE = DATA_DIR / "script.json"
BACKGROUND_LOOP = OUTPUT_DIR / "background_loop.mp4"
COVER_IMAGE = OUTPUT_DIR / "cover.jpg"
CAPTIONS_FILE = OUTPUT_DIR / "captions.srt"
FINAL_VIDEO = OUTPUT_DIR / "final_video.mp4"

WORDS_PER_CAPTION = 5


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_voice_file():
    mp3 = OUTPUT_DIR / "voice.mp3"
    wav = OUTPUT_DIR / "voice.wav"
    if mp3.exists():
        return mp3
    if wav.exists():
        return wav
    raise FileNotFoundError("No voice.mp3/voice.wav found in output/ — run generate_voice.py first")


def get_audio_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def strip_tags(script_text):
    return re.sub(r"\[[^\]]+\]", "", script_text).strip()


def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def build_captions(clean_text, duration):
    words = clean_text.split()
    total_words = len(words)
    chunks = [
        words[i:i + WORDS_PER_CAPTION]
        for i in range(0, total_words, WORDS_PER_CAPTION)
    ]

    lines = []
    word_cursor = 0
    for idx, chunk in enumerate(chunks, start=1):
        start_time = (word_cursor / total_words) * duration
        word_cursor += len(chunk)
        end_time = (word_cursor / total_words) * duration

        lines.append(str(idx))
        lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
        lines.append(" ".join(chunk))
        lines.append("")

    with open(CAPTIONS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def fetch_book_cover(book):
    query = quote(f"intitle:{book['title']} inauthor:{book['author']}")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    thumbnail = data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
    img_response = requests.get(thumbnail, timeout=20)
    img_response.raise_for_status()

    with open(COVER_IMAGE, "wb") as f:
        f.write(img_response.content)


def fetch_cover_fallback(book):
    """Offline/no-match placeholder: a simple card with the book title on it."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (500, 750), color=(235, 230, 220))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 480, 730], outline=(40, 40, 40), width=4)
    # Basic word-wrapped title text (no external font dependency)
    words = book["title"].split()
    lines, current = [], ""
    for w in words:
        test = f"{current} {w}".strip()
        if len(test) > 18:
            lines.append(current)
            current = w
        else:
            current = test
    lines.append(current)

    y = 300
    for line in lines:
        draw.text((60, y), line, fill=(20, 20, 20))
        y += 40
    draw.text((60, y + 30), f"by {book['author']}", fill=(80, 80, 80))

    img.save(COVER_IMAGE, "JPEG", quality=90)
    print(f"[offline demo] wrote placeholder cover card for {book['title']}")


def extend_background(duration):
    extended = OUTPUT_DIR / "background_extended.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(BACKGROUND_LOOP),
        "-t", str(duration),
        "-c", "copy",
        str(extended),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return extended


def assemble(background_path, cover_path, audio_path):
    filter_complex = (
        "[2:a]showwaves=s=800x120:mode=cline:colors=white:scale=lin[wave];"
        "[0:v][wave]overlay=x=(main_w-overlay_w)/2:y=main_h-160[bg1];"
        "[1:v]scale=380:-1[coverscaled];"
        "[bg1][coverscaled]overlay=x=main_w-overlay_w-60:y=60[bg2];"
        f"[bg2]subtitles={CAPTIONS_FILE}:force_style="
        "'FontName=Arial,FontSize=20,PrimaryColour=&HFFFFFF&,"
        "OutlineColour=&H000000&,BorderStyle=1,Outline=2,"
        "Alignment=2,MarginV=40'[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(background_path),
        "-loop", "1", "-i", str(cover_path),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        str(FINAL_VIDEO),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    book = load_json(SELECTED_FILE)
    script_data = load_json(SCRIPT_FILE)
    audio_path = find_voice_file()

    duration = get_audio_duration(audio_path)
    clean_text = strip_tags(script_data["script"])
    build_captions(clean_text, duration)

    try:
        fetch_book_cover(book)
        print(f"Book cover fetched for: {book['title']}")
    except Exception as e:
        print(f"[warning] Google Books fetch failed ({e}), using placeholder cover.")
        fetch_cover_fallback(book)

    extended_bg = extend_background(duration)
    assemble(extended_bg, COVER_IMAGE, audio_path)

    print(f"Final video ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    main()
