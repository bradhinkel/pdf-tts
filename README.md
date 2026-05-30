# PDF Reader — Web-based PDF-to-Speech

> **Teaching demo (frozen).** This is the simple reference version, used as a hands-on
> "first build with Claude" project. It is intentionally kept small and stable. Active
> development (multi-user auth, mobile app, design pass) continues in a separate repo.

A self-hosted web app that converts PDF documents to spoken audio.

I built this because I was having Claude generate PDF summaries of books, articles, and technical ideas — and I wanted a simple way to listen to them. Upload a PDF, hit play, and listen.

## What it is

A FastAPI backend + React frontend you deploy on any Linux server. Upload PDFs through the browser, stream them as audio. Works well on iPhone via Safari, or wrapped as a native iOS app (see V2 below).

---

## TTS backends — pick your tier

### Piper (recommended starting point)
**Free, self-hosted, no account needed.**

Open-source TTS that runs entirely on your server. Voice quality is functional — clearly intelligible, somewhat robotic. Good enough to evaluate the app and start listening. Requires no API keys.

```bash
# No extra setup — Piper installs with the app and downloads its voice model on first use
pip install -r requirements.txt
```

Endpoint: `/api/stream-audio?filename=example.pdf` (default — no flag needed)

### Azure TTS (recommended for regular use)
**~$4–5 per 1 million characters. Excellent voice quality.**

Neural voices that sound natural. You need an Azure account and a Speech Services resource (free tier covers light use). Set two environment variables and it works.

```bash
AZURE_TTS_KEY=your_key_here
AZURE_TTS_REGION=eastus   # or your region
```

Endpoint: `/api/stream-audio?filename=example.pdf&tts=azure` (opt-in via flag). In the web player, append `?tts=azure` to the page URL.

Cost reality: a 300-page book summary is roughly 150,000 characters — about $0.60. For personal use this is negligible.

### XTTS-v2 (experimental, best open-source quality)
**Free, self-hosted, best voice. Harder to run.**

Coqui XTTS-v2 produces voices that rival Azure — natural prosody, no robotic artifacts. The tradeoff is setup complexity and resource requirements. Needs Python 3.11, PyTorch, and ~2 GB of VRAM or significant CPU time.

See [XTTS setup notes](docs/xtts-setup.md) for the full dependency story.

Endpoint: `/api/stream-audio?filename=example.pdf&tts=xtts`

---

## Quick start

### Requirements
- Python 3.12+ (3.11 required only for XTTS)
- A Linux server (DigitalOcean, Linode, etc.) or local machine
- Node 18+ (to build the frontend)

### Deploy

```bash
git clone https://github.com/bradhinkel/pdf-tts.git
cd pdf-tts

# Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Azure key if using Azure TTS

# Frontend
cd frontend && npm install && npm run build && cd ..

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For production deployment (systemd + nginx + Let's Encrypt), see the production layout below.

### Environment variables

```bash
# Azure TTS (leave blank to use Piper)
AZURE_TTS_KEY=
AZURE_TTS_REGION=eastus
AZURE_TTS_VOICE=en-US-AriaNeural

# Piper TTS
PIPER_VOICE=en_US-lessac-medium
# PIPER_MODEL_DIR=/opt/pdf-tts/models/piper  # defaults to app/models/piper

# Storage
# PDF_STORAGE_PATH=/opt/pdf-tts/pdfs         # defaults to app/pdfs
MAX_PDF_SIZE=100000000
```

---

## Production layout (DigitalOcean / Ubuntu 24.04)

This repo runs on a single droplet alongside unrelated apps. Pattern:

```
/opt/pdf-tts/
  venv/                    # Python virtualenv
  app/                     # FastAPI source
  frontend/dist/           # Compiled React (served by FastAPI)
  pdfs/                    # Uploaded PDFs
  models/piper/            # Piper voice model (auto-downloaded)
  .env                     # Secrets, not in repo
```

**systemd service:** `pdf-tts-backend.service` — uvicorn on `127.0.0.1:8000`

**nginx:** reverse proxy to `:8000`, `proxy_buffering off` for audio streaming

**SSL:** Let's Encrypt via certbot

---

## V2 — iOS App (Capacitor)

The React frontend can be wrapped as a native iOS app using Capacitor. The app shell loads `reader.bradhinkel.com` — no local bundling needed.

**What Claude Code sets up (done):**
- `frontend/capacitor.config.json` — app ID, bundle URL, iOS settings
- Capacitor packages added to `frontend/package.json`

**What you do on a Mac with Xcode:**

```bash
cd frontend
npm install
npx cap add ios          # generates the Xcode project
npm run cap:sync         # builds frontend and syncs to iOS
npm run cap:open         # opens Xcode
```

In Xcode:
1. Set your Apple Developer Team under Signing & Capabilities
2. Set bundle identifier: `com.bradhinkel.pdfreader`
3. Build and run on device or simulator
4. Submit to TestFlight or App Store

Requirements: Mac, Xcode 15+, Apple Developer account ($99/year for App Store).

---

## Architecture

```
Browser / iOS App
      │
      ▼
nginx (reader.bradhinkel.com)
      │
      ▼
FastAPI :8000
  ├── /                    React SPA (static)
  ├── /api/list-pdfs       List uploaded PDFs
  ├── /api/upload          Upload a PDF
  ├── /api/pdf/{name}      Delete a PDF
  └── /api/stream-audio    Stream audio (Azure / Piper / XTTS)
         │         │              │
      Azure      Piper         XTTS-v2
      (REST)   (local .onnx)  (local model)
```
