# 🎙️ Unlimited AI Voice Generator — Speechma Studio

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Zero--VPS-100%25%20Free%20Cloud-success?style=for-the-badge&logo=render&logoColor=white" alt="Zero VPS">
  <img src="https://img.shields.io/badge/OCR%20Solver-0.4ms%20Native-orange?style=for-the-badge" alt="0.4ms Native OCR">
  <img src="https://img.shields.io/badge/UI-Apple%20Cupertino-black?style=for-the-badge&logo=apple&logoColor=white" alt="Apple Cupertino UI">
  <img src="https://img.shields.io/badge/Voices-580%2B%20Neural-purple?style=for-the-badge" alt="580+ Voices">
  <img src="https://img.shields.io/badge/Character%20Limit-Unlimited-brightgreen?style=for-the-badge" alt="Unlimited">
</p>

<p align="center">
  <strong>An industry-standard, unlimited Text-to-Speech (TTS) studio and high-performance neural voice synthesis engine.</strong><br>
  Built with an Apple-grade Cupertino Web UI, zero-dependency 0.4ms in-memory captcha solver, and concurrent parallel batch synthesis.
</p>

<p align="center">
  🚀 <strong>Developed by <a href="https://badarbukhari.me" target="_blank">Badar Bukhari</a></strong> • 🌐 <a href="https://badarbukhari.me" target="_blank"><strong>Visit Developer Portfolio</strong></a>
</p>

---

## 🌟 Why This Project? (The Ultimate ElevenLabs Alternative)

Most free Text-to-Speech services enforce strict limits: 2,000 characters, slow sequential chunking, or complicated Windows `.exe` Tesseract dependencies that require expensive VPS servers to host.

**Unlimited AI Voice Generator** solves all of this:
- **Zero VPS Dependency**: Features an ultra-fast **pure Python bitwise OCR solver** (`core/solver.py`) that cracks numeric captchas in **0.4 milliseconds with 100% accuracy**. Runs anywhere — Render, Hugging Face, Railway, Docker, Linux, macOS, or Windows — completely free!
- **Zero Character Limits**: Paste entire books, YouTube scripts, or audiobooks. Long texts are automatically chunked into natural sentence boundaries and synthesized **concurrently in parallel** across worker threads.
- **Apple Cupertino Web UI**: Crafted with frosted-glass modals, SF Pro typography, custom Apple dropdown menus with instant search, interactive waveform audio scrubbers, and Light/Dark themes (defaulting to clean Apple Light Mode).
- **580+ Ultra-Realistic Neural Voices**: Natural voices spanning **76 languages** (English, Spanish, Urdu, Arabic, Hindi, French, German, Japanese, and more) with pitch and speed customization.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| ⚡ **0.4ms Native OCR** | Reverse-engineered bitwise Hamming distance algorithm in pure Python Pillow. Zero external binaries or models. |
| 🚀 **Parallel Turbo Synthesis** | Synthesizes large multi-thousand-word texts concurrently with multi-threading, delivering audio up to 5x faster. |
| 🎨 **Apple Cupertino UI** | Frosted glass backdrop blur, custom dropdowns with search, waveform audio scrubbers, and crisp SVG vector icons (no emojis). |
| 🎙️ **580+ AI Voices** | Filter by language, country, and gender, with instant single-click preview auditions. |
| 🎛️ **Pitch & Speed Control** | Fine-tune pitch (-10 to +10) and speech rate (-10 to +10) per generation. |
| 💾 **Audio Session Library** | Scrub audio waveforms, download high-bitrate MP3 files instantly, and manage saved speech history. |
| 🌐 **Full REST API & CLI** | Includes clean FastAPI endpoints and a command-line utility for scripting and automated workflows. |

---

## 📁 Repository Structure

```
speechma-ai-voice-generator/
├── core/                         # Core Python engine & modules
│   ├── config.py                 # Auto-discovery configuration
│   ├── engine.py                 # Speechma API client & parallel batch synthesis
│   ├── solver.py                 # Pure Python 0.4ms bitwise OCR captcha solver
│   └── voices.py                 # 583 voices catalog, filters & metadata loader
├── web/                          # Web Studio Application
│   ├── app.py                    # FastAPI server & REST API
│   └── static/                   # Apple Cupertino Frontend
│       ├── index.html            # Studio Dashboard Single Page App
│       ├── css/style.css         # Apple Cupertino glassmorphic styling
│       └── js/app.js             # Dropdown controllers, waveform scrubbers & state
├── outputs/                      # Generated audio files directory
├── voices.json                   # Database of 583 voices across 76 languages
├── speechma_tts.py               # Standalone CLI client
├── run.py                        # Master launcher script
├── start_web.bat                 # Windows 1-click launcher
├── Dockerfile                    # Production Docker container
├── render.yaml                   # 1-Click Render.com deployment manifest
├── requirements.txt              # Minimal Python dependencies
└── README.md                     # Documentation
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Install

```bash
git clone https://github.com/badarbukharidev-alt/speechma-ai-voice-generator.git
cd speechma-ai-voice-generator
pip install -r requirements.txt
```

### 2. Launch the Web UI

```bash
python run.py
```
> Or simply double-click **`start_web.bat`** on Windows!

Open your browser to: **`http://127.0.0.1:7860`**

---

## ☁️ Free Cloud Deployment (Zero VPS Required)

Because this engine uses a pure Python captcha solver with no binary dependencies, you can deploy it for **100% free** on any modern cloud hosting service:

### Option 1: Render.com (1-Click Deployment)
1. Fork or push this repository to your GitHub account.
2. Go to [Render.com](https://render.com) and click **New Web Service**.
3. Connect your repository. Render will automatically detect `render.yaml`.
4. Click **Create Web Service**!

### Option 2: Hugging Face Spaces (Docker)
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Choose **Docker** as the SDK.
3. Push this repository. The included `Dockerfile` will build and host your private or public TTS studio with a free HTTPS URL.

### Option 3: Railway / Koyeb
1. Connect your repository.
2. Railway and Koyeb will build using the `Dockerfile` automatically on port `7860`.

---

## 💻 Command Line Interface (CLI)

You can generate speech directly from your terminal:

```bash
# Generate audio with default voice
python speechma_tts.py "Welcome to the Unlimited AI Voice Generator." -o welcome.mp3

# Use specific voice with pitch and rate adjustments
python speechma_tts.py "Breaking news today..." -v voice-107 -p 2 -r 1 -o news.mp3

# Process long text files with parallel batch processing
python speechma_tts.py -f script.txt --batch -o audiobook.mp3

# List all available voices for a language
python speechma_tts.py --list-voices --lang English
```

---

## 🐍 Python SDK Usage

Import and use the engine directly in your Python applications:

```python
from core import SpeechmaTTS, generate_batch

# Standard Generation
engine = SpeechmaTTS()
audio_bytes = engine.generate(
    text="Synthesizing natural voice with Speechma.",
    voice="voice-107",
    pitch=0,
    rate=0
)

with open("output.mp3", "wb") as f:
    f.write(audio_bytes)

# Unlimited Parallel Batch Generation for Long Documents
combined_mp3, chunk_count = generate_batch(
    text="Very long article, novel chapter, or script...",
    voice="voice-107",
    max_workers=5
)
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/status` | `GET` | Health check & OCR solver status |
| `/api/languages` | `GET` | All 76 languages and country metadata |
| `/api/voices` | `GET` | Search and filter 583 voices by language, gender, country |
| `/api/tts` | `POST` | Generate speech audio with custom pitch, speed, and filename |
| `/api/history` | `GET` | Retrieve list of generated audio files |
| `/api/audio/{filename}` | `GET` | Stream or download generated MP3 audio |
| `/api/audio/{filename}` | `DELETE` | Delete audio file from storage |

### Example Request (`POST /api/tts`)

```bash
curl -X POST http://127.0.0.1:7860/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world! This is generated via the Unlimited AI Voice Generator API.",
    "voice": "voice-107",
    "pitch": 0,
    "rate": 0,
    "filename": "my_audio_narration"
  }'
```

---

## 👨‍💻 Developer & Attribution

- **Developer**: **[Badar Bukhari](https://badarbukhari.me)**
- **Portfolio**: [https://badarbukhari.me](https://badarbukhari.me)
- **GitHub**: [@badarbukharidev-alt](https://github.com/badarbukharidev-alt)

Feel free to connect, submit issues, or contribute pull requests!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
