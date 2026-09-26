"""
Automated Test Suite for Speechma Studio Web UI and Core Engine.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from web.app import app
from core import split_text_smart

client = TestClient(app)

def test_api_status():
    print("[TEST] Checking /api/status...")
    res = client.get("/api/status")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data["status"] == "online"
    assert data["tesseract"]["available"] is True
    assert data["voices_count"] > 500
    print(f"       -> OK! Tesseract: {data['tesseract']['version']}, Voices: {data['voices_count']}")

def test_api_languages():
    print("[TEST] Checking /api/languages...")
    res = client.get("/api/languages")
    assert res.status_code == 200
    data = res.json()
    assert len(data["languages"]) > 50
    print(f"       -> OK! Loaded {len(data['languages'])} languages")

def test_api_voices():
    print("[TEST] Checking /api/voices filtering...")
    # Search by keyword
    res = client.get("/api/voices?query=Andrew")
    assert res.status_code == 200
    data = res.json()
    assert any(v["name"] == "Andrew Multilingual" for v in data["voices"])
    
    # Filter by language
    res_es = client.get("/api/voices?language=Spanish")
    assert res_es.status_code == 200
    data_es = res_es.json()
    assert data_es["total"] > 30
    print(f"       -> OK! Voices search & filter works ({data_es['total']} Spanish voices found)")

def test_smart_chunker():
    print("[TEST] Checking smart text chunker...")
    short_text = "This is a short sentence."
    assert len(split_text_smart(short_text, limit=100)) == 1

    long_text = "Sentence one. " * 50  # ~700 chars
    chunks = split_text_smart(long_text, limit=200)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 200
    print(f"       -> OK! Split into {len(chunks)} chunks, all respecting limits.")

def test_api_tts_and_audio_lifecycle():
    print("[TEST] Checking /api/tts synthesis, streaming, and deletion...")
    payload = {
        "text": "Antigravity automated test verifying full functionality of the speech engine.",
        "voice": "voice-107",
        "pitch": 0,
        "rate": 0,
        "filename": "test_audio_verify"
    }
    res = client.post("/api/tts", json=payload)
    assert res.status_code == 200, f"Synthesis failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert data["size_bytes"] > 5000
    filename = data["filename"]
    print(f"       -> OK! Generated audio {filename} ({data['size_formatted']})")

    # Verify history contains file
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert any(f["filename"] == filename for f in hist_data["history"])

    # Stream audio
    audio_res = client.get(f"/api/audio/{filename}")
    assert audio_res.status_code == 200
    assert audio_res.headers["content-type"] == "audio/mpeg"

    # Delete test file
    del_res = client.delete(f"/api/audio/{filename}")
    assert del_res.status_code == 200
    print("       -> OK! Audio streamed and cleaned up successfully.")

if __name__ == "__main__":
    print("=" * 60)
    print("Running Speechma Full Test Suite")
    print("=" * 60)
    test_api_status()
    test_api_languages()
    test_api_voices()
    test_smart_chunker()
    test_api_tts_and_audio_lifecycle()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
