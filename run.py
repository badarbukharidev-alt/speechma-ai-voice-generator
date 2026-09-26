#!/usr/bin/env python3
"""
Speechma Runner - Launch the Web UI Studio or CLI
Usage:
    python run.py                   # Launches the Web UI and opens browser
    python run.py --port 8080       # Custom port
    python run.py --cli --help      # Runs the CLI interface
"""

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.config import DEFAULT_HOST, DEFAULT_PORT, HAS_TESSERACT, TESSERACT_EXE, TESSERACT_VERSION


def open_browser_delayed(url: str, delay: float = 1.2):
    """Opens web browser after a brief delay to allow server startup."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()


def start_web_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, no_browser: bool = False):
    """Starts the FastAPI Web UI via uvicorn."""
    import uvicorn

    print("=" * 60)
    print("           SPEECHMA UNLIMITED TTS STUDIO")
    print("=" * 60)
    print(f"[*] Engine Status:")
    if HAS_TESSERACT:
        print(f"    Tesseract OCR : Available ({TESSERACT_VERSION})")
        print(f"    Binary Path   : {TESSERACT_EXE}")
    else:
        print(f"    [!] Tesseract OCR : NOT FOUND. Captcha solving may fail.")
    print(f"[*] Web Server    : http://{host}:{port}")
    print("=" * 60)

    if not no_browser:
        open_browser_delayed(f"http://{host}:{port}")

    uvicorn.run("web.app:app", host=host, port=port, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="Speechma Unlimited TTS Runner")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host address (default: {DEFAULT_HOST})")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--cli", action="store_true", help="Forward to CLI tool")
    args, unknown = parser.parse_known_args()

    if args.cli:
        # Delegate to speechma_tts.py
        import speechma_tts
        sys.argv = [sys.argv[0]] + unknown
        speechma_tts.main()
    else:
        start_web_server(host=args.host, port=args.port, no_browser=args.no_browser)


if __name__ == "__main__":
    main()
