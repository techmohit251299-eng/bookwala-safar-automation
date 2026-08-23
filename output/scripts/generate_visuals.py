"""
Step 4: Generate the looping background visual for the video.

1. Builds a mood prompt from the selected book's theme and requests a
   background image from Pollinations.ai — free, no API key needed.
2. Uses ffmpeg to turn that still image into a 12-second looping clip
   with a slow zoom (Ken Burns effect) and a light blur, so it reads
   as a subtle, hazy, ever-moving background behind the book cover,
   captions, and waveform (added in the assembly step).

Output: output/background.jpg (still) and output/background_loop.mp4 (loop)
"""

import os
import subprocess
from pathlib import Path
from urllib.parse import quote

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SELECTED_FILE = DATA_DIR / "selected_book.json"
BACKGROUND_IMAGE = OUTPUT_DIR / "background.jpg"
BACKGROUND_LOOP = OUTPUT_DIR / "background_loop.mp4"

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
LOOP_SECONDS = 12


def load_selected_book():
    import json

    with open(SELECTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(book):
    return (
        f"cinematic moody dark sky and mountains, atmospheric, dramatic clouds, "
        f"minimal, evokes {book['theme']}, high detail, wide shot, "
        f"no text, no people, no watermark"
    )


def fetch_background_image(prompt):
    url = (
        f"https://image.pollinations.ai/prompt/{quote(prompt)}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(BACKGROUND_IMAGE, "wb") as f:
        f.write(response.content)


def fetch_background_fallback(book):
    """
    Offline placeholder (a simple dark gradient) so the pipeline can be
    test-run without network access. The real Pollinations.ai call in
    CI needs no API key, so this fallback should rarely be needed there.
    """
    from PIL import Image, ImageDraw

    OUTPUT_DIR.mkdir(exist_ok=True)
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    draw = ImageDraw.Draw(img)
    top = (20, 24, 38)
    bottom = (70, 55, 45)
    for y in range(IMAGE_HEIGHT):
        t = y / IMAGE_HEIGHT
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=color)
    img.save(BACKGROUND_IMAGE, "JPEG", quality=90)
    print(f"[offline demo] wrote placeholder gradient background for {book['title']}")


def make_looping_video():
    """
    Ken Burns style slow zoom + light blur, looped to LOOP_SECONDS.
    zoompan needs a high-fps intermediate then we settle on 30fps output.
    """
    filter_chain = (
        f"gblur=sigma=6,"
        f"scale=8000:-1,"
        f"zoompan=z='min(zoom+0.0007,1.15)':d={LOOP_SECONDS * 25}:s={IMAGE_WIDTH}x{IMAGE_HEIGHT}:fps=25,"
        f"format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(BACKGROUND_IMAGE),
        "-vf", filter_chain,
        "-t", str(LOOP_SECONDS),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(BACKGROUND_LOOP),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    book = load_selected_book()
    prompt = build_prompt(book)

    try:
        fetch_background_image(prompt)
        print(f"Background image fetched from Pollinations.ai for: {book['title']}")
    except Exception as e:
        print(f"[warning] Pollinations.ai fetch failed ({e}), using offline fallback.")
        fetch_background_fallback(book)

    make_looping_video()
    print(f"Looping background video ready: {BACKGROUND_LOOP}")


if __name__ == "__main__":
    main()
