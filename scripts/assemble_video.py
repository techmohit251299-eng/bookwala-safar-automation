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
    """
    New layout:
    - Background: full screen
    - Book cover: left side (scaled down)
    - Waveform: right side (vertical strip, colorful)
    - Social icons: bottom center (like, subscribe, share text)
    - Captions: bottom-left, smaller font
    """
    filter_complex = (
        # Waveform on right side (width: 120px, full height) - colorful
        "[2:a]showwaves=s=120x1080:mode=cline:colors=0xFF6B6B|0xFFFFFF|0x4ECDC4:scale=lin[wave];"
        
        # Book cover on left (smaller, width: 350px)
        "[1:v]scale=350:-1[coverscaled];"
        
        # Background + book cover on left side
        "[0:v][coverscaled]overlay=x=50:y=100[bg1];"
        
        # Add waveform on right side
        "[bg1][wave]overlay=x=main_w-130:y=0[bg2];"
        
        # Add captions (smaller font, bottom-left) - halka chota
        f"[bg2]subtitles={CAPTIONS_FILE}:force_style="
        "'FontName=Arial,FontSize=13,PrimaryColour=&HFFFFFF&,"
        "OutlineColour=&H000000&,BorderStyle=1,Outline=1,"
        "Alignment=1,MarginL=50,MarginV=90'[bg3];"
        
        # Add social media icons text at bottom center
        "[bg3]drawtext=text='👍 LIKE     🔔 SUBSCRIBE     ↗️ SHARE':"
        "fontsize=14:fontcolor=white:x=(main_w-text_w)/2:y=main_h-40:"
        "borderw=1:bordercolor=black[vout]"
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
        "-preset", "fast",  # faster encoding
        "-c:a", "aac",
        "-shortest",
        str(FINAL_VIDEO),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    try:
        book = load_json(SELECTED_FILE)
        print(f"[LOG] Loaded book: {book['title']}")
        
        script_data = load_json(SCRIPT_FILE)
        print(f"[LOG] Loaded script")
        
        audio_path = find_voice_file()
        print(f"[LOG] Found audio: {audio_path}")
        
        duration = get_audio_duration(audio_path)
        print(f"[LOG] Audio duration: {duration} seconds")
        
        clean_text = strip_tags(script_data["script"])
        print(f"[LOG] Script cleaned, {len(clean_text)} chars")
        
        build_captions(clean_text, duration)
        print(f"[LOG] Captions built: {CAPTIONS_FILE}")
        
        try:
            fetch_book_cover(book)
            print(f"[LOG] Book cover fetched: {COVER_IMAGE}")
        except Exception as e:
            print(f"[WARNING] Google Books fetch failed ({e}), using placeholder cover.")
            fetch_cover_fallback(book)
            print(f"[LOG] Placeholder cover created: {COVER_IMAGE}")

        extended_bg = extend_background(duration)
        print(f"[LOG] Extended background: {extended_bg}")
        
        print(f"[LOG] Starting ffmpeg assembly...")
        assemble(extended_bg, COVER_IMAGE, audio_path)
        print(f"[LOG] Final video ready: {FINAL_VIDEO}")
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
