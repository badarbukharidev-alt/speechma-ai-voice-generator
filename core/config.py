"""
Configuration settings and environment discovery for Speechma TTS.
"""

import os
import shutil
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
OUTPUTS_DIR = BASE_DIR / "outputs"
VOICES_FILE = BASE_DIR / "voices.json"

# Ensure output directory exists
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Tesseract resolution
TESS_PATHS = [
    BASE_DIR / "tesseract" / "tesseract.exe",
    BASE_DIR / "tesseract.exe",
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
]

TESSERACT_EXE = None
for p in TESS_PATHS:
    if p.exists():
        TESSERACT_EXE = p
        break

if not TESSERACT_EXE:
    system_tess = shutil.which("tesseract")
    if system_tess:
        TESSERACT_EXE = Path(system_tess)

# Configure pytesseract if available
HAS_TESSERACT = False
TESSERACT_VERSION = "Not installed"

try:
    import pytesseract
    if TESSERACT_EXE:
        pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)
        # Also set TESSDATA_PREFIX if tessdata folder is alongside executable
        tessdata = TESSERACT_EXE.parent / "tessdata"
        if tessdata.exists():
            os.environ["TESSDATA_PREFIX"] = str(tessdata)
        try:
            ver = pytesseract.get_tesseract_version()
            TESSERACT_VERSION = str(ver)
            HAS_TESSERACT = True
        except Exception as e:
            TESSERACT_VERSION = f"Error: {e}"
except ImportError:
    pass

# Speechma API Constants
BASE_URL = "https://speechma.com"
CAPTCHA_URL = f"{BASE_URL}/com.api/captcha/captcha.php"
TTS_URL = f"{BASE_URL}/com.api/tts-api.php"
PREVIEW_URL_TEMPLATE = f"{BASE_URL}/assets/audio/previews/{{voice_id}}.mp3"

DEFAULT_VOICE = "voice-107"
MAX_CHARS_PER_REQUEST = 2000

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/english",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# Web Server defaults
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7860
