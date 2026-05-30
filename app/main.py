import asyncio
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.config import MAX_PDF_SIZE, PDF_STORAGE_PATH, XTTS_SPEAKER
from app.pdf_processor import chunk_text, extract_text
from app.tts_service import synthesize_chunk

app = FastAPI(title="PDF TTS")

PDF_DIR = Path(PDF_STORAGE_PATH)
PDF_DIR.mkdir(parents=True, exist_ok=True)


def _safe_path(filename: str) -> Path:
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Not a PDF file")
    return PDF_DIR / filename


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── PDF management ────────────────────────────────────────────────────────────

@app.get("/api/list-pdfs")
async def list_pdfs():
    pdfs = sorted(
        (
            {"name": f.name, "size": f.stat().st_size}
            for f in PDF_DIR.glob("*.pdf")
            if f.is_file()
        ),
        key=lambda x: x["name"],
    )
    return {"pdfs": pdfs}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    if len(content) > MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 100 MB limit")

    dest = PDF_DIR / Path(file.filename).name
    if dest.exists():
        raise HTTPException(status_code=409, detail="A file with that name already exists")

    dest.write_bytes(content)
    return {"filename": dest.name, "size": dest.stat().st_size}


@app.delete("/api/pdf/{filename}")
async def delete_pdf(filename: str):
    path = _safe_path(filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    path.unlink()
    return {"deleted": filename}


# ── Audio streaming ───────────────────────────────────────────────────────────

@app.get("/api/stream-audio")
async def stream_audio(filename: str, tts: str = "piper"):
    pdf_path = _safe_path(filename)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    text = extract_text(pdf_path)
    chunks = chunk_text(text)

    if tts == "piper":
        from app.piper_service import synthesize_all as piper_synth
        try:
            audio = await asyncio.get_event_loop().run_in_executor(
                None, piper_synth, chunks
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Piper error: {exc}")
        return Response(content=audio, media_type="audio/wav")

    if tts == "xtts":
        import traceback
        from app.xtts_service import synthesize_all
        try:
            audio = await synthesize_all(chunks, speaker=XTTS_SPEAKER)
        except Exception as exc:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"XTTS error: {exc}")
        return Response(content=audio, media_type="audio/wav")

    # Azure streaming (opt-in via tts=azure)
    async def generate():
        for chunk in chunks:
            try:
                yield await synthesize_chunk(chunk)
            except Exception as exc:
                print(f"TTS error skipping chunk: {exc}")

    return StreamingResponse(generate(), media_type="audio/mpeg")


# ── Frontend (must be last) ───────────────────────────────────────────────────

_static = Path(__file__).parent.parent / "frontend" / "dist"
if _static.exists():
    app.mount("/", StaticFiles(directory=_static, html=True), name="static")
