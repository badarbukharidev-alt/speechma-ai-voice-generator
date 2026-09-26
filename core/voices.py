"""
Voice management, catalog querying, and filtering for Speechma TTS.
"""

import json
from typing import Dict, List, Optional
from core.config import VOICES_FILE, PREVIEW_URL_TEMPLATE, DEFAULT_VOICE

_VOICES_CACHE: Optional[List[Dict[str, str]]] = None

# Built-in fallback voices in case voices.json is missing or corrupted
FALLBACK_VOICES = [
    {"id": "voice-107", "name": "Andrew Multilingual", "gender": "Male", "language": "Multilingual", "country": "United States"},
    {"id": "voice-110", "name": "Ava Multilingual", "gender": "Female", "language": "Multilingual", "country": "United States"},
    {"id": "voice-112", "name": "Brian Multilingual", "gender": "Male", "language": "Multilingual", "country": "United States"},
    {"id": "voice-115", "name": "Emma Multilingual", "gender": "Female", "language": "Multilingual", "country": "United States"},
    {"id": "voice-1", "name": "Jenny", "gender": "Female", "language": "English", "country": "United States"},
    {"id": "voice-2", "name": "Guy", "gender": "Male", "language": "English", "country": "United States"},
    {"id": "voice-5", "name": "Aria", "gender": "Female", "language": "English", "country": "United States"},
    {"id": "voice-10", "name": "Davis", "gender": "Male", "language": "English", "country": "United States"},
    {"id": "voice-20", "name": "Jane", "gender": "Female", "language": "English", "country": "United States"},
    {"id": "voice-50", "name": "Jason", "gender": "Male", "language": "English", "country": "United States"},
    {"id": "voice-100", "name": "Sara", "gender": "Female", "language": "English", "country": "United States"},
    {"id": "voice-150", "name": "Tony", "gender": "Male", "language": "English", "country": "United States"},
    {"id": "voice-200", "name": "Nancy", "gender": "Female", "language": "English", "country": "United States"},
]


def load_voices() -> List[Dict[str, str]]:
    """Loads all voices from voices.json or fallback list, caching the result."""
    global _VOICES_CACHE
    if _VOICES_CACHE is not None:
        return _VOICES_CACHE

    raw_voices = []
    if VOICES_FILE.exists():
        try:
            with open(VOICES_FILE, "r", encoding="utf-8") as f:
                raw_voices = json.load(f)
        except Exception as e:
            print(f"[Warning] Failed to load {VOICES_FILE}: {e}")
            raw_voices = FALLBACK_VOICES
    else:
        raw_voices = FALLBACK_VOICES

    # Ensure preview_url is present on all items
    processed = []
    for v in raw_voices:
        voice = dict(v)
        if "preview_url" not in voice:
            voice["preview_url"] = PREVIEW_URL_TEMPLATE.format(voice_id=voice["id"])
        processed.append(voice)

    _VOICES_CACHE = processed
    return _VOICES_CACHE


def get_all_voices() -> List[Dict[str, str]]:
    return load_voices()


def get_voice_by_id(voice_id: str) -> Optional[Dict[str, str]]:
    resolved = resolve_voice_id(voice_id)
    for v in load_voices():
        if v["id"] == resolved:
            return v
    return None


def resolve_voice_id(voice: str) -> str:
    """Normalize input like '107' or 'voice-107' to standard 'voice-107' format."""
    voice = str(voice).strip()
    if voice.isdigit():
        return f"voice-{voice}"
    if not voice.startswith("voice-") and any(c.isdigit() for c in voice):
        # e.g. "107"
        return f"voice-{voice}"
    return voice or DEFAULT_VOICE


def get_languages() -> List[Dict[str, any]]:
    """Returns sorted list of unique languages with count of available voices."""
    voices = load_voices()
    counts: Dict[str, int] = {}
    for v in voices:
        lang = v.get("language", "Unknown")
        counts[lang] = counts.get(lang, 0) + 1

    sorted_langs = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [{"language": lang, "count": count} for lang, count in sorted_langs]


def get_genders() -> List[str]:
    voices = load_voices()
    return sorted(list({v.get("gender", "Unknown") for v in voices}))


def get_countries() -> List[str]:
    voices = load_voices()
    return sorted(list({v.get("country", "Unknown") for v in voices if v.get("country")}))


def filter_voices(
    query: Optional[str] = None,
    language: Optional[str] = None,
    gender: Optional[str] = None,
    country: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Filter voices by search query, language, gender, or country."""
    voices = load_voices()
    results = []

    q = query.lower().strip() if query else None
    l = language.lower().strip() if language and language != "all" else None
    g = gender.lower().strip() if gender and gender != "all" else None
    c = country.lower().strip() if country and country != "all" else None

    for v in voices:
        if l and v.get("language", "").lower() != l:
            continue
        if g and v.get("gender", "").lower() != g:
            continue
        if c and v.get("country", "").lower() != c:
            continue
        if q:
            name = v.get("name", "").lower()
            vid = v.get("id", "").lower()
            lang = v.get("language", "").lower()
            country_name = v.get("country", "").lower()
            if q not in name and q not in vid and q not in lang and q not in country_name:
                continue
        results.append(v)

    return results
