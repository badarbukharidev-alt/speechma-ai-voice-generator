"""
Speechma TTS Core Package
"""

from core.config import HAS_TESSERACT, TESSERACT_EXE, TESSERACT_VERSION, OUTPUTS_DIR
from core.engine import SpeechmaTTS, SpeechmaError, CaptchaError, TTSError, split_text_smart, generate_batch
from core.proxy import proxy_manager, ProxyManager
from core.voices import (
    load_voices,
    get_all_voices,
    get_voice_by_id,
    get_languages,
    get_genders,
    get_countries,
    filter_voices,
    resolve_voice_id,
)

__all__ = [
    "SpeechmaTTS",
    "SpeechmaError",
    "CaptchaError",
    "TTSError",
    "split_text_smart",
    "generate_batch",
    "HAS_TESSERACT",
    "TESSERACT_EXE",
    "TESSERACT_VERSION",
    "OUTPUTS_DIR",
    "load_voices",
    "get_all_voices",
    "get_voice_by_id",
    "get_languages",
    "get_genders",
    "get_countries",
    "filter_voices",
    "resolve_voice_id",
]
