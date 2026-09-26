"""
Speechma Web Application - FastAPI Server
Provides REST APIs for Text-to-Speech synthesis, voice discovery, audio streaming, and history management.
"""

import base64
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core import (
    HAS_TESSERACT,
    OUTPUTS_DIR,
    TESSERACT_EXE,
    TESSERACT_VERSION,
    SpeechmaTTS,
    filter_voices,
    generate_batch,
    get_all_voices,
    get_countries,
    get_genders,
    get_languages,
    get_voice_by_id,
    resolve_voice_id,
    split_text_smart,
)
from core.config import BASE_DIR, STATIC_DIR

app = FastAPI(
    title="Speechma Unlimited TTS",
    description="Local unlimited TTS web interface powered by local Tesseract OCR.",
    version="2.0.0",
)

# Enable CORS for flexible local development and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Models
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to convert to speech")
    voice: str = Field(default="voice-107", description="Voice ID or shortcut")
    pitch: int = Field(default=0, ge=-10, le=10, description="Pitch offset (-10 to 10)")
    rate: int = Field(default=0, ge=-10, le=10, description="Rate offset (-10 to 10)")
    filename: Optional[str] = Field(default=None, description="Optional custom filename")
    manual_code: Optional[str] = Field(default=None, description="Manual captcha code if solving manually")
    request_id: Optional[str] = Field(default=None, description="Manual captcha requestId")


class CaptchaVerifyRequest(BaseModel):
    code: str
    request_id: str


@app.get("/api/status")
def get_system_status():
    """Returns engine health, solver status, and voice count."""
    voices = get_all_voices()
    return {
        "status": "online",
        "solver": "pure_python_ultra_fast",
        "vps_required": False,
        "tesseract": {
            "available": HAS_TESSERACT,
            "version": TESSERACT_VERSION,
            "path": str(TESSERACT_EXE) if TESSERACT_EXE else None,
        },
        "voices_count": len(voices),
        "languages_count": len(get_languages()),
        "outputs_count": len(list(OUTPUTS_DIR.glob("*.mp3"))),
    }


@app.get("/api/voices")
def get_voices(
    query: Optional[str] = Query(None, description="Search term for name or id"),
    language: Optional[str] = Query(None, description="Filter by language"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    country: Optional[str] = Query(None, description="Filter by country"),
):
    """Returns voice catalog with optional filtering."""
    filtered = filter_voices(query=query, language=language, gender=gender, country=country)
    return {
        "total": len(filtered),
        "voices": filtered,
    }


@app.get("/api/languages")
def get_language_list():
    """Returns all available languages and voice counts."""
    return {
        "languages": get_languages(),
        "genders": get_genders(),
        "countries": get_countries(),
    }


@app.get("/api/captcha/new")
def get_new_captcha():
    """Fetches a fresh captcha image and request ID for manual or visual inspection."""
    engine = SpeechmaTTS()
    try:
        img_bytes, rid = engine.fetch_captcha()
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        # Try local OCR as a hint
        hint = ""
        if HAS_TESSERACT:
            try:
                hint = engine.solve_captcha_image(img_bytes)
            except Exception:
                hint = ""

        return {
            "success": True,
            "request_id": rid,
            "image_data": f"data:image/png;base64,{b64}",
            "ocr_hint": hint,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
def synthesize_tts(req: TTSRequest):
    """
    Main TTS endpoint. Converts text to speech, supporting texts of any length.
    Automatically segments long texts (>2000 chars) into fluent chunks.
    """
    cleaned_text = req.text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    engine = SpeechmaTTS()
    voice_id = resolve_voice_id(req.voice)
    voice_info = get_voice_by_id(voice_id) or {
        "id": voice_id,
        "name": voice_id,
        "gender": "Unknown",
        "language": "Unknown",
    }

    timestamp = int(time.time())
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sanitize custom filename if provided
    if req.filename and req.filename.strip():
        safe_name = re.sub(r"[^\w\-_.]", "_", req.filename.strip())
        if not safe_name.lower().endswith(".mp3"):
            safe_name += ".mp3"
        out_filename = f"{date_str}_{safe_name}"
    else:
        # e.g. speechma_20260927_012000_voice-107.mp3
        out_filename = f"speechma_{date_str}_{voice_id}.mp3"

    out_path = OUTPUTS_DIR / out_filename

    try:
        # Determine if single request or batch needed
        chunks = split_text_smart(cleaned_text, limit=2000)

        if len(chunks) == 1 and not (req.manual_code and req.request_id):
            # Single standard generation
            audio_bytes = engine.generate(
                text=chunks[0],
                voice=voice_id,
                pitch=req.pitch,
                rate=req.rate,
                max_retries=6,
            )
        elif req.manual_code and req.request_id:
            # Manual captcha code supplied
            audio_bytes = engine.generate(
                text=chunks[0],
                voice=voice_id,
                pitch=req.pitch,
                rate=req.rate,
                manual_code=req.manual_code,
                request_id=req.request_id,
            )
        else:
            # Multi-chunk batch generation
            audio_bytes, _ = generate_batch(
                engine=engine,
                text=cleaned_text,
                voice=voice_id,
                pitch=req.pitch,
                rate=req.rate,
            )

        # Save audio file to disk
        out_path.write_bytes(audio_bytes)

        return {
            "success": True,
            "filename": out_filename,
            "url": f"/api/audio/{out_filename}",
            "download_url": f"/api/audio/{out_filename}?download=1",
            "size_bytes": len(audio_bytes),
            "size_formatted": f"{len(audio_bytes) / 1024:.1f} KB",
            "voice": voice_info,
            "chunks_count": len(chunks),
            "character_count": len(cleaned_text),
            "text_preview": cleaned_text[:120] + ("..." if len(cleaned_text) > 120 else ""),
            "created_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audio/{filename}")
def get_audio_file(filename: str, download: bool = False):
    """Streams or downloads an audio file from the outputs directory."""
    # Prevent directory traversal
    safe_name = os.path.basename(filename)
    file_path = OUTPUTS_DIR / safe_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{safe_name}"'
    else:
        headers["Content-Disposition"] = f'inline; filename="{safe_name}"'

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=safe_name if download else None,
        headers=headers,
    )


@app.get("/api/history")
def get_history():
    """Lists generated audio files sorted by creation time descending."""
    files = []
    for f in OUTPUTS_DIR.glob("*.mp3"):
        try:
            stat = f.stat()
            size = stat.st_size
            created = datetime.fromtimestamp(stat.st_mtime)
            files.append({
                "filename": f.name,
                "url": f"/api/audio/{f.name}",
                "download_url": f"/api/audio/{f.name}?download=1",
                "size_bytes": size,
                "size_formatted": f"{size / 1024:.1f} KB",
                "timestamp": stat.st_mtime,
                "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception:
            continue

    files.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"total": len(files), "history": files}


@app.delete("/api/audio/{filename}")
def delete_audio_file(filename: str):
    """Deletes a generated audio file from outputs."""
    safe_name = os.path.basename(filename)
    file_path = OUTPUTS_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    try:
        file_path.unlink()
        return {"success": True, "message": f"Deleted {safe_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {e}")


# Mount static assets for frontend UI
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    """Serves the main single-page web UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return JSONResponse(
        content={
            "message": "Speechma API is running. Place index.html into web/static/ to view UI.",
            "docs": "/docs",
        }
    )
