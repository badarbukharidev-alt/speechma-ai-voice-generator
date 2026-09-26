"""
Speechma TTS Engine with automatic local Tesseract OCR captcha solving,
smart chunking for unlimited text, and robust retry logic.
"""

import base64
import json
import logging
import random
import re
import string
import time
from io import BytesIO
from pathlib import Path
from typing import Callable, List, Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image

from core.config import (
    CAPTCHA_URL,
    DEFAULT_VOICE,
    HAS_TESSERACT,
    MAX_CHARS_PER_REQUEST,
    REQUEST_HEADERS,
    TESSERACT_EXE,
    TTS_URL,
)
from core.solver import solve_captcha_pure_python
from core.voices import resolve_voice_id

logger = logging.getLogger("speechma.engine")

try:
    import pytesseract
except ImportError:
    pytesseract = None


class SpeechmaError(Exception):
    """Base exception for Speechma TTS operations."""
    pass


class CaptchaError(SpeechmaError):
    """Raised when captcha solving or verification fails."""
    pass


class TTSError(SpeechmaError):
    """Raised when TTS generation API returns an error."""
    pass


class SpeechmaTTS:
    """Core Speechma TTS client with captcha handling and audio generation."""

    def __init__(self, timeout: int = 120):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.timeout = timeout

    def _generate_rid(self) -> str:
        """Generates a random request id matching the format expected by Speechma."""
        ts = int(time.time() * 1000)
        rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"{ts}_{rand}"

    def fetch_captcha(self) -> Tuple[bytes, str]:
        """Fetches a captcha challenge image and request ID from Speechma."""
        rid = self._generate_rid()
        rand_part = rid.split("_")[1]
        try:
            resp = self.session.get(
                CAPTCHA_URL,
                params={"t": str(int(time.time() * 1000)), "r": rand_part},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.content, rid
        except Exception as e:
            raise CaptchaError(f"Failed to fetch captcha from Speechma: {e}") from e

    def verify_captcha(self, code: str, request_id: str) -> bool:
        """Submits the solved captcha code for verification."""
        payload = {"code": str(code).strip(), "requestId": request_id}
        try:
            resp = self.session.post(
                CAPTCHA_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("success") is True
        except Exception as e:
            logger.warning(f"Captcha verification request error: {e}")
            return False

    def solve_captcha_image(self, img_bytes: bytes) -> str:
        """
        Solves the 5-digit Speechma captcha.
        Tries ultra-fast pure Python bitmask matcher first (<1ms, zero external dependencies).
        Falls back to Tesseract OCR if available.
        """
        try:
            code = solve_captcha_pure_python(img_bytes)
            if len(code) == 5:
                return code
        except Exception as e:
            logger.debug(f"Pure python solver exception: {e}")

        # Fallback to local Tesseract OCR if available
        if HAS_TESSERACT and pytesseract is not None:
            try:
                img = Image.open(BytesIO(img_bytes)).convert("L")
                img = img.point(lambda x: 0 if x < 140 else 255)
                config = "--psm 7 -c tessedit_char_whitelist=0123456789"
                raw_text = pytesseract.image_to_string(img, config=config).strip()
                digits = "".join(c for c in raw_text if c.isdigit())
                if len(digits) == 5:
                    return digits[:5]
            except Exception as e:
                logger.warning(f"Tesseract OCR fallback failed: {e}")

        raise CaptchaError("Captcha solver could not resolve 5-digit code.")

    def request_tts(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        pitch: int = 0,
        rate: int = 0,
    ) -> bytes:
        """Calls the Speechma TTS API for a verified session."""
        if len(text) > MAX_CHARS_PER_REQUEST:
            raise ValueError(
                f"Text exceeds {MAX_CHARS_PER_REQUEST} characters limit ({len(text)} given). "
                "Use batch generation for longer texts."
            )

        voice = resolve_voice_id(voice)
        payload = {
            "text": text,
            "voice": voice,
            "pitch": int(pitch),
            "rate": int(rate),
        }

        try:
            resp = self.session.post(
                TTS_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise TTSError(f"TTS network request failed: {e}") from e

        content_type = resp.headers.get("content-type", "").lower()
        if content_type.startswith("audio/") or "mpeg" in content_type or resp.content.startswith(b"\xff\xfb") or resp.content.startswith(b"ID3"):
            return resp.content

        # Handle non-audio response (error JSON or HTML)
        try:
            err_json = resp.json()
            raise TTSError(f"Speechma API returned error: {err_json}")
        except json.JSONDecodeError:
            raise TTSError(
                f"Unexpected response from Speechma (status {resp.status_code}): {resp.text[:250]}"
            )

    def generate(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        pitch: int = 0,
        rate: int = 0,
        max_retries: int = 6,
        status_callback: Optional[Callable[[dict], None]] = None,
        manual_code: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> bytes:
        """
        Generates TTS audio for text <= 2000 characters with automated captcha solving.
        
        Args:
            text: Text to speak (max 2000 chars)
            voice: Voice ID (e.g. 'voice-107')
            pitch: Pitch offset (-10 to 10)
            rate: Speech rate offset (-10 to 10)
            max_retries: Number of captcha retry attempts
            status_callback: Optional callback receiving dict with progress/status
            manual_code: Optional manual captcha code if user provided one
            request_id: Optional request_id corresponding to manual_code
        """
        voice = resolve_voice_id(voice)

        # If manual captcha code and request_id provided
        if manual_code and request_id:
            if status_callback:
                status_callback({"step": "verifying_manual", "code": manual_code})
            if not self.verify_captcha(manual_code, request_id):
                raise CaptchaError("Manual captcha code verification failed")
            if status_callback:
                status_callback({"step": "synthesizing", "voice": voice})
            return self.request_tts(text, voice=voice, pitch=pitch, rate=rate)

        # Automatic OCR flow
        last_error = None
        for attempt in range(1, max_retries + 1):
            if status_callback:
                status_callback({
                    "step": "captcha_attempt",
                    "attempt": attempt,
                    "max_retries": max_retries,
                    "message": f"Fetching captcha (attempt {attempt}/{max_retries})...",
                })

            try:
                img_bytes, rid = self.fetch_captcha()
            except Exception as e:
                last_error = e
                time.sleep(0.5)
                continue

            try:
                code = self.solve_captcha_image(img_bytes)
            except Exception as e:
                last_error = e
                code = ""

            if len(code) != 5:
                if status_callback:
                    status_callback({
                        "step": "ocr_retry",
                        "attempt": attempt,
                        "code": code,
                        "message": f"OCR detected invalid length '{code}', retrying...",
                    })
                time.sleep(0.6)
                continue

            if status_callback:
                status_callback({
                    "step": "verifying_ocr",
                    "attempt": attempt,
                    "code": code,
                    "message": f"OCR solved code '{code}', verifying with Speechma...",
                })

            if not self.verify_captcha(code, rid):
                if status_callback:
                    status_callback({
                        "step": "ocr_failed_verify",
                        "attempt": attempt,
                        "code": code,
                        "message": f"Code '{code}' was rejected, trying new captcha...",
                    })
                time.sleep(0.6)
                continue

            # Captcha verified! Now generate speech
            if status_callback:
                status_callback({
                    "step": "synthesizing",
                    "attempt": attempt,
                    "voice": voice,
                    "message": "Captcha verified successfully! Synthesizing audio...",
                })

            audio_data = self.request_tts(text, voice=voice, pitch=pitch, rate=rate)
            if status_callback:
                status_callback({
                    "step": "completed",
                    "bytes": len(audio_data),
                    "message": "Speech generated successfully.",
                })
            return audio_data

        raise CaptchaError(f"All {max_retries} captcha attempts failed. Last error: {last_error}")


def split_text_smart(text: str, limit: int = MAX_CHARS_PER_REQUEST) -> List[str]:
    """
    Intelligently splits long text into chunks <= limit chars at sentence or paragraph boundaries.
    """
    text = text.strip()
    if len(text) <= limit:
        return [text]

    # Split into paragraphs first
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: List[str] = []
    current_buf = ""

    for paragraph in paragraphs:
        # If single paragraph fits in current buffer
        candidate = (current_buf + "\n\n" + paragraph).strip() if current_buf else paragraph
        if len(candidate) <= limit:
            current_buf = candidate
            continue

        # If current buffer has content, flush it
        if current_buf:
            chunks.append(current_buf.strip())
            current_buf = ""

        # If paragraph itself is within limit, use it
        if len(paragraph) <= limit:
            current_buf = paragraph
            continue

        # Paragraph exceeds limit, split into sentences
        # Match sentence endings: . ! ? followed by whitespace or end of string
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            candidate = (current_buf + " " + sentence).strip() if current_buf else sentence
            if len(candidate) <= limit:
                current_buf = candidate
            else:
                if current_buf:
                    chunks.append(current_buf.strip())
                    current_buf = ""
                # If a single sentence is longer than limit, hard split by words
                if len(sentence) > limit:
                    words = sentence.split(" ")
                    for word in words:
                        sub_cand = (current_buf + " " + word).strip() if current_buf else word
                        if len(sub_cand) <= limit:
                            current_buf = sub_cand
                        else:
                            if current_buf:
                                chunks.append(current_buf.strip())
                            current_buf = word
                else:
                    current_buf = sentence

    if current_buf:
        chunks.append(current_buf.strip())

    return chunks


def generate_batch(
    engine: Optional[SpeechmaTTS] = None,
    text: str = "",
    voice: str = DEFAULT_VOICE,
    pitch: int = 0,
    rate: int = 0,
    progress_callback: Optional[Callable[[dict], None]] = None,
    max_workers: int = 5,
) -> Tuple[bytes, List[bytes]]:
    """
    Processes long text in parallel chunks using ThreadPoolExecutor
    and joins the resulting MP3 audio data in the exact original sequence.
    Returns (combined_audio_bytes, list_of_chunk_audio_bytes).
    """
    chunks = split_text_smart(text)
    total_chunks = len(chunks)
    if total_chunks == 0:
        return b"", []
    if total_chunks == 1:
        eng = engine or SpeechmaTTS()
        audio = eng.generate(chunks[0], voice=voice, pitch=pitch, rate=rate)
        return audio, [audio]

    ordered_results: List[Optional[bytes]] = [None] * total_chunks
    completed_chunks = 0
    lock = threading.Lock()
    workers_count = min(max_workers, total_chunks)

    if progress_callback:
        progress_callback({
            "step": "parallel_batch_start",
            "total_chunks": total_chunks,
            "workers": workers_count,
            "message": f"Generating {total_chunks} chunks concurrently with {workers_count} parallel workers...",
        })

    def process_single_chunk(item: Tuple[int, str]) -> Tuple[int, bytes]:
        nonlocal completed_chunks
        idx, chunk_text = item
        # Each worker thread must use its own isolated SpeechmaTTS session instance
        worker_engine = SpeechmaTTS(timeout=engine.timeout if engine else 120)
        
        audio = worker_engine.generate(
            text=chunk_text,
            voice=voice,
            pitch=pitch,
            rate=rate,
            max_retries=6,
        )

        with lock:
            completed_chunks += 1
            curr_completed = completed_chunks

        if progress_callback:
            progress_callback({
                "chunk_index": idx + 1,
                "total_chunks": total_chunks,
                "completed": curr_completed,
                "progress_percent": int((curr_completed / total_chunks) * 100),
                "message": f"Parallel synthesis: {curr_completed}/{total_chunks} chunks completed...",
            })

        return idx, audio

    with ThreadPoolExecutor(max_workers=workers_count) as executor:
        futures = [
            executor.submit(process_single_chunk, (i, ch))
            for i, ch in enumerate(chunks)
        ]
        for future in as_completed(futures):
            idx, chunk_audio = future.result()
            ordered_results[idx] = chunk_audio

    # Verify all chunks were processed
    chunk_audios: List[bytes] = [r for r in ordered_results if r is not None]
    if len(chunk_audios) != total_chunks:
        raise TTSError(f"Parallel batch generation incomplete: {len(chunk_audios)}/{total_chunks} chunks succeeded.")

    # Seamlessly concatenate standard MP3 frames in exact sequential order
    combined = b"".join(chunk_audios)

    if progress_callback:
        progress_callback({
            "step": "completed",
            "total_chunks": total_chunks,
            "bytes": len(combined),
            "progress_percent": 100,
            "message": f"All {total_chunks} chunks finished in parallel! ({len(combined)} bytes total).",
        })

    return combined, chunk_audios
