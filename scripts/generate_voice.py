"""
Voice Generation - Philosopher Style with ALL MAPPINGS (FIXED)
Proper error handling + debugging included
"""

import os
from pathlib import Path
import json
import re
import sys

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCRIPT_FILE = DATA_DIR / "script.json"
VOICE_OUTPUT = OUTPUT_DIR / "voice.mp3"

# PHILOSOPHER VOICE SETTINGS
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# CHUNK SIZE RANGE
MIN_CHUNK_CHARS = 2000
MAX_CHUNK_CHARS = 3000
TARGET_CHUNK_CHARS = 2500

VOICE_SEED = 42
PAUSE_DURATION = 800

# ═══════════════════════════════════════════════════════════
# ALL MAPPINGS (Hinglish Pronunciation + Devanagari)
# ═══════════════════════════════════════════════════════════

DEVANAGARI_MAPPINGS = {
    "Aristotle": "अरिस्टोटल (Aristotle)",
    "Plato": "प्लेटो (Plato)",
    "Nietzsche": "नीत्शे (Nietzsche)",
    "Socrates": "सुकरात (Socrates)",
    "Descartes": "डेकार्ट (Descartes)",
}

AUTHOR_MAPPINGS = {
    "Aristotle": "अरिस्टोटल (Aristotle)",
    "Plato": "प्लेटो (Plato)",
    "Socrates": "सुकरात (Socrates)",
    "Nietzsche": "नीत्शे (Nietzsche)",
    "Descartes": "डेसकार्ट (Descartes)",
    "Viktor Frankl": "विक्टर फ्रैंकल (Viktor Frankl)",
    "James Clear": "जेम्स क्लियर (James Clear)",
    "Cal Newport": "कैल न्यूपोर्ट (Cal Newport)",
    "Stephen Covey": "स्टीफन कोवी (Stephen Covey)",
    "Robert Greene": "रॉबर्ट ग्रीन (Robert Greene)",
    "Dale Carnegie": "डेल कार्नेगी (Dale Carnegie)",
    "Napoleon Hill": "नेपोलियन हिल (Napoleon Hill)",
    "Tony Robbins": "टोनी रॉबिन्स (Tony Robbins)",
    "Robin Sharma": "रॉबिन शर्मा (Robin Sharma)",
    "Simon Sinek": "साइमन सिनेक (Simon Sinek)",
    "Ryan Holiday": "रयान हॉलिडे (Ryan Holiday)",
    "Mark Manson": "मार्क मैनसन (Mark Manson)",
    "Daniel Kahneman": "डैनियल काह्नमन (Daniel Kahneman)",
    "Morgan Housel": "मॉर्गन हाउसल (Morgan Housel)",
    "Adam Grant": "एडम ग्रांट (Adam Grant)",
    "Naval Ravikant": "नवल रविकांत (Naval Ravikant)"
}

BOOK_MAPPINGS = {
    "Atomic Habits": "एटॉमिक हैबिट्स (Atomic Habits)",
    "The 7 Habits of Highly Effective People": "द सेवन हैबिट्स ऑफ हाईली इफेक्टिव पीपल",
    "Think and Grow Rich": "थिंक एंड ग्रो रिच",
    "Rich Dad Poor Dad": "रिच डैड पुअर डैड",
    "The Psychology of Money": "द साइकोलॉजी ऑफ मनी",
}

CONCEPT_MAPPINGS = {
    "discipline": "अनुशासन (discipline)",
    "consistency": "निरंतरता (consistency)",
    "motivation": "प्रेरणा (motivation)",
    "procrastination": "टालमटोल (procrastination)",
    "self-discipline": "आत्म-अनुशासन (self-discipline)",
    "confidence": "आत्मविश्वास (confidence)",
    "mindset": "मानसिकता (mindset)",
}

BUSINESS_MAPPINGS = {
    "wealth": "धन-संपत्ति (wealth)",
    "income": "आय (income)",
    "investment": "निवेश (investment)",
    "financial freedom": "वित्तीय स्वतंत्रता (financial freedom)",
}

PHILOSOPHY_MAPPINGS = {
    "philosophy": "दर्शन (philosophy)",
    "stoicism": "स्टोइक दर्शन (Stoicism)",
    "ethics": "नीतिशास्त्र (ethics)",
    "meaning": "अर्थ (meaning)",
}

PSYCHOLOGY_MAPPINGS = {
    "dopamine": "डोपामिन (dopamine)",
    "confidence": "आत्मविश्वास (confidence)",
    "decision making": "निर्णय लेने की प्रक्रिया (decision making)",
}

NARRATION_MAPPINGS = {
    "however": "लेकिन",
    "therefore": "इसलिए",
    "because": "क्योंकि",
}

# COMBINE ALL MAPPINGS
ALL_MAPPINGS = {
    **DEVANAGARI_MAPPINGS,
    **AUTHOR_MAPPINGS,
    **BOOK_MAPPINGS,
    **CONCEPT_MAPPINGS,
    **BUSINESS_MAPPINGS,
    **PHILOSOPHY_MAPPINGS,
    **PSYCHOLOGY_MAPPINGS,
    **NARRATION_MAPPINGS,
}


# ═══════════════════════════════════════════════════════════
# FIX #1: PROPER DEPENDENCY CHECK
# ═══════════════════════════════════════════════════════════
def check_dependencies():
    """Check if all required packages are installed."""
    print("\n🔍 Checking dependencies...")
    
    dependencies = {
        'elevenlabs': 'ElevenLabs API client',
        'pydub': 'Audio processing',
        'dotenv': 'Environment variables (optional but recommended)',
    }
    
    missing = []
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"  ✅ {package}: {description}")
        except ImportError:
            print(f"  ❌ {package}: {description} - MISSING!")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        print(f"\n📝 Also install ffmpeg:")
        print(f"   Ubuntu: sudo apt-get install ffmpeg")
        print(f"   Mac: brew install ffmpeg")
        print(f"   Windows: choco install ffmpeg\n")
        return False
    
    print("  ✅ All dependencies OK!\n")
    return True


# ═══════════════════════════════════════════════════════════
# FIX #2: ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════
def verify_environment():
    """Verify API keys and paths."""
    print("🔐 Verifying environment setup...\n")
    
    # Check API Key
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not set!")
        print("   Set it with:")
        print("   export ELEVENLABS_API_KEY='your-key-here'")
        print("   Or in .env file\n")
        return False
    else:
        print(f"  ✅ ELEVENLABS_API_KEY: {api_key[:10]}...{api_key[-5:]}")
    
    # Check data directory
    if not DATA_DIR.exists():
        print(f"❌ Data directory not found: {DATA_DIR}")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"   Created: {DATA_DIR}\n")
        return False
    else:
        print(f"  ✅ Data directory: {DATA_DIR}")
    
    # Check script file
    if not SCRIPT_FILE.exists():
        print(f"❌ Script file not found: {SCRIPT_FILE}")
        print("   Create a script.json with:")
        print('   {"book": "Atomic Habits", "script": "Your text here..."}\n')
        return False
    else:
        print(f"  ✅ Script file: {SCRIPT_FILE}")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ Output directory: {OUTPUT_DIR}\n")
    
    return True


# ═══════════════════════════════════════════════════════════
# FIX #3: BETTER MAPPING APPLICATION
# ═══════════════════════════════════════════════════════════
def add_all_mappings_to_text(text):
    """Add ALL mappings to text with better handling."""
    modified_text = text
    
    print(f"\n  📝 Applying {len(ALL_MAPPINGS)} mappings...")
    applied = 0
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_mappings = sorted(ALL_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for english, hindi in sorted_mappings:
        # Case-insensitive replacement - word boundaries
        pattern = re.compile(r'\b' + re.escape(english) + r'\b', re.IGNORECASE)
        before = modified_text.count(english)
        modified_text = pattern.sub(hindi, modified_text)
        after = modified_text.count(hindi)
        
        if after > before:
            applied += 1
    
    print(f"  ✅ Applied: {applied} unique mappings\n")
    return modified_text


# ═══════════════════════════════════════════════════════════
# FIX #4: BETTER CHUNKING LOGIC
# ═══════════════════════════════════════════════════════════
def smart_chunk_text_range(text, min_chars=MIN_CHUNK_CHARS, max_chars=MAX_CHUNK_CHARS, target_chars=TARGET_CHUNK_CHARS):
    """
    SMART CHUNKING (2000-3000 char range):
    1. Split by paragraphs
    2. Combine until in range
    3. If too long, split by sentences
    """
    
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    if not paragraphs:
        return [text] if text else []
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        test_length = len(test_chunk)
        
        # If test chunk is within range, use it
        if min_chars <= test_length <= max_chars:
            current_chunk = test_chunk
        
        # If test chunk is too long
        elif test_length > max_chars:
            # Save current chunk if valid
            if current_chunk and len(current_chunk) >= min_chars:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If paragraph itself is too long, split by sentences
            if len(paragraph) > max_chars:
                sentences = [s.strip() for s in paragraph.split(". ") if s.strip()]
                sentence_chunk = ""
                
                for i, sentence in enumerate(sentences):
                    # Add period if missing
                    piece = sentence if sentence.endswith(".") else sentence
                    piece += ". " if i < len(sentences) - 1 else "."
                    
                    sentence_chunk_test = sentence_chunk + " " + piece if sentence_chunk else piece
                    
                    if len(sentence_chunk_test) <= max_chars:
                        sentence_chunk = sentence_chunk_test
                    else:
                        if sentence_chunk and len(sentence_chunk) >= min_chars:
                            chunks.append(sentence_chunk.strip())
                        sentence_chunk = piece
                
                if sentence_chunk and len(sentence_chunk) >= min_chars:
                    chunks.append(sentence_chunk.strip())
            
            else:
                # Paragraph is small enough
                current_chunk = paragraph
        
        else:
            # Test chunk is too small, keep accumulating
            current_chunk = test_chunk
    
    # Add final chunk
    if current_chunk and len(current_chunk) >= min_chars:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]


# ═══════════════════════════════════════════════════════════
# FIX #5: BETTER ERROR HANDLING IN VOICE GENERATION
# ═══════════════════════════════════════════════════════════
def generate_with_elevenlabs_all_mappings(script_text, voice_id):
    """Voice generation with ALL MAPPINGS + PROPER ERROR HANDLING."""
    
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings
        from pydub import AudioSegment
        import io
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install: pip install elevenlabs pydub")
        return False

    # ADD ALL MAPPINGS
    print("\n📝 Adding Hinglish Pronunciations...")
    script_text = add_all_mappings_to_text(script_text)
    
    # CHUNK TEXT
    chunks = smart_chunk_text_range(script_text, MIN_CHUNK_CHARS, MAX_CHUNK_CHARS, TARGET_CHUNK_CHARS)

    print(f"\n🎙️ PHILOSOPHER VOICE GENERATION (ALL MAPPINGS)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📝 Script: {len(script_text)} characters")
    print(f"📦 Chunks: {len(chunks)} pieces")
    print(f"🗺️  Mappings: {len(ALL_MAPPINGS)} total")
    print(f"🎙️ Voice ID: {voice_id}")
    print(f"🔒 Seed: {VOICE_SEED} (LOCKED)")
    print(f"📏 Range: {MIN_CHUNK_CHARS}-{MAX_CHUNK_CHARS} chars")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    try:
        client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    except Exception as e:
        print(f"❌ API Client Error: {e}")
        print("   Check your ELEVENLABS_API_KEY\n")
        return False

    combined = AudioSegment.empty()
    successful_chunks = 0

    # Generate each chunk
    for idx, chunk in enumerate(chunks, start=1):
        chunk_words = len(chunk.split())
        chunk_chars = len(chunk)
        
        print(f"  [{idx}/{len(chunks)}] Chunk ({chunk_chars} chars, {chunk_words} words)...", end="", flush=True)
        
        try:
            # Make API call with error handling
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=chunk,
                model_id="eleven_multilingual_v2",  # Better for Hinglish
                seed=VOICE_SEED,
                voice_settings=VoiceSettings(
                    stability=0.78,
                    similarity_boost=0.85,
                    style=0.12,
                    use_speaker_boost=False,
                ),
            )

            audio_bytes = b"".join(audio_stream)
            
            if not audio_bytes:
                print(" ⚠️  Empty audio received")
                continue
            
            segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            combined += segment
            successful_chunks += 1
            
            print(" ✅")

            if idx < len(chunks):
                combined += AudioSegment.silent(duration=PAUSE_DURATION)
                
        except Exception as e:
            print(f" ❌")
            print(f"     Error: {str(e)[:100]}")
            print(f"     Check:")
            print(f"     - API key validity")
            print(f"     - Rate limits (wait a minute)")
            print(f"     - Text length and content")
            continue

    if successful_chunks == 0:
        print("\n❌ No chunks generated successfully!")
        return False

    # Export
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        combined.export(VOICE_OUTPUT, format="mp3", bitrate="128k")

        duration_min = len(combined) / 1000 / 60
        print(f"\n{'━'*70}")
        print(f"✅ Voice generation complete!")
        print(f"📊 Total duration: {duration_min:.1f} minutes")
        print(f"✅ Successful chunks: {successful_chunks}/{len(chunks)}")
        print(f"📁 Saved: {VOICE_OUTPUT}")
        print(f"🗺️  Applied: {len(ALL_MAPPINGS)} mappings")
        print(f"{'━'*70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Export error: {e}\n")
        return False


def main():
    """Main flow with better error handling."""
    
    print("\n" + "="*70)
    print("GROW WITH BOOKS - VOICE WITH ALL MAPPINGS")
    print("="*70)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Step 3: Load script
    try:
        with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        script_text = data.get("script", "")
        
        if not script_text:
            print("❌ Script is empty!\n")
            sys.exit(1)
            
        print(f"📚 Book: {data.get('book', 'Unknown')}")
        print(f"✍️  Script length: {len(script_text)} characters\n")
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in script.json: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading script: {e}\n")
        sys.exit(1)
    
    # Step 4: Get voice ID
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    print(f"🎙️ Voice ID: {voice_id}\n")

    # Step 5: Generate voice
    try:
        success = generate_with_elevenlabs_all_mappings(script_text, voice_id)
        if success:
            print("🎉 SUCCESS! Voice with all mappings ready!\n")
        else:
            print("❌ Voice generation failed. Check errors above.\n")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
