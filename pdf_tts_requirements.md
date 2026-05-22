# PDF-to-Speech Streaming Webapp
## Multi-Phase Implementation Plan

---

## Project Overview

Build a web application that converts PDF documents to speech via streaming audio, with progressive feature expansion from a minimal V0 proof-of-concept through a native iOS wrapper. The application runs on a DigitalOcean droplet and is accessed via Safari on iPhone.

**Core Principle:** Each phase is deployable and functional independently. V0 validates the text extraction → TTS streaming pipeline. V1 adds production UX and file management. V1.5 experiments with open-source TTS quality. V2 wraps everything in an iOS container.

---

## V0: Minimal PDF-to-Speech Streamer
**Goal:** Validate the text extraction, chunking, and Azure TTS streaming pipeline with zero frontend complexity.

### Backend Requirements

**Stack:** Python 3.11+, FastAPI, Azure SDK, pdfplumber, uvicorn

**Architecture:**
- Single FastAPI application listening on port 8000
- Reads a PDF file from a static directory (`/app/pdfs/`)
- Extracts full text via pdfplumber
- Chunks text into sentences (use nltk or simple regex split on `. `)
- Calls Azure Cognitive Services TTS for each chunk
- Streams audio chunks back to client as a single MP3 stream

**Azure TTS Integration:**
- Use Azure Cognitive Services Speech service (Standard tier)
- Endpoint: `https://<region>.tts.speech.microsoft.com/cognitiveservices/v1`
- API key from Azure portal
- Voice: Default US English voice (e.g., `en-US-AriaNeural`)
- Audio format: MP3 (audio-16khz-128kbitrate-mono-mp3)
- Request format: SSML or plain text via REST

**Key Endpoints:**

```
GET /health
  Response: {"status": "ok"}

GET /api/list-pdfs
  Response: {"pdfs": ["filename1.pdf", "filename2.pdf"]}

GET /api/stream-audio?filename=example.pdf
  Response: Stream of MP3 audio (Content-Type: audio/mpeg)
  Behavior: Extracts text, chunks by sentence, streams TTS audio sequentially
  Error handling: Return 404 if file not found, 500 if TTS call fails
```

**Text Chunking Strategy:**
- Split on sentence boundaries (`. ` followed by space and capital letter)
- Minimum chunk size: 10 words, maximum 200 words (to keep TTS latency reasonable per chunk)
- Preserve paragraph breaks in logic (optional pause between chunks)

**Implementation Details for Claude Code:**
- Create `/app/main.py` with FastAPI app
- Create `/app/config.py` with Azure credentials (read from environment variables)
- Create `/app/tts_service.py` with Azure TTS client and streaming logic
- Create `/app/pdf_processor.py` with pdfplumber extraction and chunking
- Create `/app/requirements.txt` with dependencies: fastapi, uvicorn, pdfplumber, azure-cognitiveservices-speech, nltk
- Deployment: gunicorn + uvicorn on DigitalOcean droplet (port 8000 behind nginx reverse proxy)

---

## V1: Full-Featured Webapp with File Management & Piper TTS
**Goal:** Add complete UX, file upload/delete, player controls, and switch to open-source Piper TTS.

### Frontend Requirements

**Stack:** React 18, Tailwind CSS, simple state management (useState/useContext)

**Key Components:**
- **FileUploadZone:** Drag-drop interface for PDF upload, progress indicator
- **FileList:** Table showing uploaded PDFs with size, delete button, "Play" action
- **AudioPlayer:** Custom controls (play/pause, progress slider, volume, current time/duration)
- **NowPlaying:** Show currently playing file name, current sentence/chunk (optional)

**Functionality:**
- Upload PDF (POST to `/api/upload`)
- List PDFs (GET `/api/list-pdfs`)
- Delete PDF (DELETE `/api/pdf/{filename}`)
- Play PDF audio (GET `/api/stream-audio?filename=X` with standard HTML5 `<audio>` element)
- Player state persists across page navigation (e.g., resume if you close and reopen)

**Technical Details:**
- Single-page React app (index.html, App.jsx, components folder)
- Tailwind for styling (minimal custom CSS)
- HTML5 native audio element for playback (no third-party player library)
- localStorage to remember last played file and timestamp

### Backend Changes for V1

**New Endpoints:**

```
POST /api/upload
  Body: multipart/form-data with file field
  Response: {"filename": "uploaded_name.pdf", "size": 1024000}
  Behavior: Validate PDF, save to /app/pdfs/, reject if exists or >100MB

DELETE /api/pdf/{filename}
  Response: {"deleted": "filename.pdf"}
  Behavior: Remove file, validate filename safe (no path traversal)
```

**Piper TTS Integration:**
- Replace Azure TTS calls with Piper
- Piper runs as a subprocess or via a Python library (`piper-tts`)
- Voice: English US female (default; check available voices)
- Audio output: WAV format (simpler streaming than MP3)
- Latency: ~1-2 seconds per chunk on a 2GB+ machine

**Implementation Details for Claude Code:**
- Refactor TTS service: create `/app/piper_service.py` with Piper integration
- Move PDF directory from static to `/app/pdfs/` with write permissions
- Add file validation (MIME type, size limits)
- Update `/app/main.py` to add `/api/upload` and `/api/pdf/{filename}` endpoints
- Frontend: Create `/frontend/src` structure with React components
- Build frontend: Use Vite or Create React App for dev/build pipeline
- Serve frontend from FastAPI static files (or separate nginx)
- Update `/app/requirements.txt`: add piper-tts, python-multipart

**Deployment:**
- DigitalOcean droplet: Python backend + frontend assets (compiled React)
- Install Piper TTS on droplet: `pip install piper-tts`
- Download Piper voice model(s) on startup or manually

---

## V1.5: Experiment with XTTS-v2
**Goal:** Test whether XTTS-v2 provides meaningfully better prosody/naturalness than Piper.

### Technical Approach

**XTTS-v2 Integration:**
- Use `TTS` library from Coqui (pip install `TTS`)
- Load quantized model (int8) to fit on 4GB memory with margin
- Model: `tts_models/multilingual/multi-speaker/xtts_v2`
- Architecture: GPU acceleration preferred but CPU-fallback acceptable
- Voice: Can clone from a sample audio file or use default speakers

**Implementation Details for Claude Code:**
- Create `/app/xtts_service.py` with XTTS-v2 client
- Add flag/toggle to choose TTS backend (Piper vs XTTS-v2) via environment variable or query param
- Parallel implementation: Both services run; switch via `/api/stream-audio?filename=X&tts=xtts` or similar
- No frontend changes needed for basic A/B testing
- Monitor memory usage; if droplet struggles, fall back to Piper

**Metrics to Compare:**
- Latency (seconds per chunk)
- Naturalness (subjective listening)
- Memory footprint
- CPU usage during generation

**If Successful:**
- Make XTTS-v2 the default TTS backend
- Remove Piper code in future cleanup
- If too slow/heavy, revert to Piper for production

---

## V2: iOS App Wrapper (Capacitor)
**Goal:** Package the webapp as a native iOS application for submission to App Store.

### Technical Approach

**Stack:** Capacitor (framework for wrapping web apps as native mobile apps)

**Architecture:**
- Capacitor wraps the existing React web app
- Deploys to iOS via Xcode
- Runs inside a WKWebView (WebKit) with native iOS features accessible
- Backend API stays on DigitalOcean (no mobile backend needed)

**Implementation Details for Claude Code:**
- Initialize Capacitor project: `npx cap init` in existing React app
- Add iOS platform: `npx cap add ios`
- Configure Capacitor (`capacitor.config.json`): set API endpoint URL, permissions
- Build React app for production: `npm run build`
- Copy build output to Capacitor: `npx cap copy ios`
- Generate Xcode project: `npx cap open ios`

**At this stage, you take over on Mac:**
- Open Xcode project generated above
- Configure bundle identifier (com.yourname.pdfreader)
- Add Apple Developer Team signing
- Build for simulator or device
- Test locally on iPhone (development)
- Generate provisioning profiles and certificates for TestFlight submission
- Submit to App Store (requires Apple Developer account)

**Capacitor Plugins to Consider (optional):**
- `@capacitor/filesystem` - if you want to store PDFs locally on device
- `@capacitor/share` - share audio/PDFs via system share sheet
- `@capacitor/statusbar` - control iOS status bar appearance
- For V2, stick to basics; additional plugins are nice-to-have

**Requirements for You (Post-Claude Code):**
- Mac with Xcode 14+
- Apple Developer account ($99/year for App Store)
- Understanding of provisioning profiles, certificates, bundle IDs
- TestFlight for beta testing before App Store submission

**Deployment Path:**
1. Claude Code creates Capacitor scaffold + Xcode project
2. You open in Xcode on Mac
3. You configure signing and build settings
4. You build and test on device
5. You submit to App Store via Xcode or App Store Connect

---

## File Structure

```
/app
  ├── main.py                 # FastAPI application
  ├── config.py              # Environment, Azure/Piper config
  ├── tts_service.py         # Azure TTS client (V0/V1)
  ├── piper_service.py       # Piper TTS client (V1+)
  ├── xtts_service.py        # XTTS-v2 client (V1.5+)
  ├── pdf_processor.py       # pdfplumber extraction + chunking
  ├── requirements.txt       # Python dependencies
  ├── pdfs/                  # User-uploaded PDFs (created at runtime)
  └── static/                # Compiled React build output (V1+)

/frontend                     # React app (V1+)
  ├── src/
  │   ├── App.jsx
  │   ├── components/
  │   │   ├── FileUploadZone.jsx
  │   │   ├── FileList.jsx
  │   │   └── AudioPlayer.jsx
  │   ├── index.css
  │   └── main.jsx
  ├── package.json
  ├── vite.config.js         # or Create React App config
  └── index.html

/capacitor                    # Capacitor + iOS project (V2)
  ├── capacitor.config.json
  ├── ios/                   # Xcode project (generated)
  └── android/               # Android project (bonus; not required)
```

---

## Environment Variables

```
# V0/V1: Azure TTS
AZURE_TTS_KEY=<your-api-key>
AZURE_TTS_REGION=<region-e.g.-eastus>
AZURE_TTS_VOICE=en-US-AriaNeural

# V1+: Piper TTS
PIPER_VOICE=en_US-lessac-medium  # Or other available voice

# V1.5+: XTTS-v2 TTS
XTTS_MODEL_PATH=/path/to/model  # Or auto-download on first run
XTTS_ENABLED=true               # Toggle between Piper/XTTS

# General
BACKEND_URL=http://localhost:8000  # Used in frontend config
MAX_PDF_SIZE=100000000             # 100MB limit
PDF_STORAGE_PATH=/app/pdfs
```

---

## Success Criteria by Phase

**V0:** Navigate to `http://localhost:8000/api/stream-audio?filename=test.pdf` in browser, hear audio stream start within 5 seconds, full PDF reads naturally.

**V1:** Upload a PDF via web UI, click play, hear audio with proper player controls, delete removes file from list and disk.

**V1.5:** Toggle between Piper and XTTS-v2, perceive meaningful difference in naturalness/prosody, droplet stays stable at ~20-30% CPU/memory.

**V2:** Build Xcode project successfully, run in iOS simulator or on device, access webapp via app wrapper, submit to TestFlight.

---

## Notes

- **Streaming Strategy:** For V0/V1, generate full audio upfront and stream from disk. Only optimize chunked real-time generation if you feel latency.
- **PDF Handling:** Large PDFs (100+ pages) will generate 200+ chunks. Expect full generation in 30-60 seconds before audio playback starts. This is acceptable for personal use.
- **Azure Costs:** V0 testing will cost pennies. Monitor usage; Standard tier is ~$4-5 per 1M characters.
- **Open Source TTS on Droplet:** Piper and XTTS-v2 require model downloads (300MB–2GB each). Plan disk space.
- **iOS Distribution:** App Store submission requires Apple review. Expect 1-3 days turnaround. Testflight beta is instant.

