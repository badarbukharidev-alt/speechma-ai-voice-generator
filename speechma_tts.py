#!/usr/bin/env python3
"""
Speechma Unlimited TTS CLI Client
Uses local Tesseract OCR in ./tesseract/ to automatically solve numeric captchas.
Now backed by the modular `core` package with full access to 580+ voices.
"""

import argparse
import base64
import sys
import time
from pathlib import Path
from typing import List, Optional

# Ensure project root is in python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import core
from core import (
    HAS_TESSERACT,
    OUTPUTS_DIR,
    TESSERACT_EXE,
    TESSERACT_VERSION,
    SpeechmaTTS,
    filter_voices,
    generate_batch,
    get_all_voices,
    get_voice_by_id,
    resolve_voice_id,
    split_text_smart,
)
from core.config import DEFAULT_VOICE

# Backward compatibility alias
VOICES = {
    "1": "voice-1",
    "2": "voice-2",
    "5": "voice-5",
    "10": "voice-10",
    "20": "voice-20",
    "50": "voice-50",
    "100": "voice-100",
    "107": "voice-107",
    "150": "voice-150",
    "200": "voice-200",
}


class Speechma(SpeechmaTTS):
    """
    Backward-compatible Speechma class wrapper around core.SpeechmaTTS.
    """
    def __init__(self, timeout: int = 120):
        super().__init__(timeout=timeout)

    def solve_tesseract(self, img_bytes: bytes) -> str:
        return self.solve_captcha_image(img_bytes)

    def tts(self, text: str, voice: str = DEFAULT_VOICE, pitch: int = 0, rate: int = 0) -> bytes:
        return self.request_tts(text=text, voice=voice, pitch=pitch, rate=rate)


def split_text(text: str, limit: int = 2000) -> List[str]:
    return split_text_smart(text, limit=limit)


def main():
    p = argparse.ArgumentParser(
        description="Speechma unlimited TTS - local tesseract, no account"
    )
    p.add_argument("text", nargs="*", help="Text to speak (or use --file)")
    p.add_argument("-f", "--file", type=Path, help="Read text from file")
    p.add_argument("-o", "--output", type=Path, default=Path("out.mp3"), help="Output MP3")
    p.add_argument("-v", "--voice", default=DEFAULT_VOICE, help="Voice id (e.g. voice-107 or 107)")
    p.add_argument("--pitch", type=int, default=0, help="Pitch offset (-10 to 10)")
    p.add_argument("--rate", type=int, default=0, help="Rate offset (-10 to 10)")
    p.add_argument("--manual", action="store_true", help="Force manual captcha entry")
    p.add_argument("--save-captcha", type=Path, default=None, help="Save captcha image path")
    p.add_argument("--retries", type=int, default=6, help="Captcha retry count")
    p.add_argument("--list-voices", action="store_true", help="Show available voices")
    p.add_argument("--lang", type=str, default=None, help="Filter voices by language with --list-voices")
    p.add_argument("--batch", action="store_true", help="Split long text into <=2000 char chunks")
    p.add_argument("--check-tess", action="store_true", help="Only test local tesseract")
    args = p.parse_args()

    if args.check_tess:
        if not HAS_TESSERACT:
            print("FAIL: pytesseract or tesseract.exe not found")
            print(f"Expected binary: {TESSERACT_EXE or 'None'}")
            sys.exit(1)
        print(f"OK  tesseract {TESSERACT_VERSION}")
        print(f"    binary -> {TESSERACT_EXE}")
        return

    if args.list_voices:
        voices = filter_voices(language=args.lang) if args.lang else get_all_voices()
        print(f"Voices catalog ({len(voices)} available):")
        for v in voices[:30]:
            print(f"  {v['id']:<10} | {v['name']:<22} | {v['language']:<12} | {v['gender']}")
        if len(voices) > 30:
            print(f"  ... and {len(voices) - 30} more voices. Use --lang <Language> to filter or launch the Web UI!")
        return

    if args.file:
        text = args.file.read_text(encoding="utf-8").strip()
    else:
        text = " ".join(args.text).strip()

    if not text:
        text = "Hello from Speechma unlimited client running on Windows."

    voice = resolve_voice_id(args.voice)
    voice_info = get_voice_by_id(voice)
    voice_name = voice_info['name'] if voice_info else voice

    print(f"[*] Voice: {voice} ({voice_name}) | Text length: {len(text)} characters")

    sm = Speechma()
    chunks = split_text(text) if (args.batch or len(text) > 2000) else [text[:2000]]
    out_base = args.output

    if len(chunks) == 1:
        mp3 = sm.generate(
            chunks[0],
            voice=voice,
            pitch=args.pitch,
            rate=args.rate,
            max_retries=args.retries,
            manual_code=None,
        )
        out_base.write_bytes(mp3)
        print(f"[+] Success! {len(mp3)} bytes -> {out_base.resolve()}")
    else:
        print(f"[*] Batch processing {len(chunks)} chunks...")
        combined_audio, chunk_audios = generate_batch(
            engine=sm,
            text=text,
            voice=voice,
            pitch=args.pitch,
            rate=args.rate,
            progress_callback=lambda p: print(f"    {p.get('message', '')}"),
        )
        out_base.write_bytes(combined_audio)
        print(f"[+] All {len(chunks)} chunks joined! {len(combined_audio)} bytes -> {out_base.resolve()}")


if __name__ == "__main__":
    main()