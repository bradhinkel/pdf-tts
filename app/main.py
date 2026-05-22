from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.config import PDF_STORAGE_PATH
from app.pdf_processor import chunk_text, extract_text
from app.tts_service import synthesize_chunk

app = FastAPI(title="PDF TTS")

PDF_DIR = Path(PDF_STORAGE_PATH)
PDF_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/list-pdfs")
async def list_pdfs():
    pdfs = sorted(f.name for f in PDF_DIR.glob("*.pdf") if f.is_file())
    return {"pdfs": pdfs}


@app.get("/api/stream-audio")
async def stream_audio(filename: str):
    # Guard against path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    pdf_path = PDF_DIR / filename
    if not pdf_path.exists() or not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found")
    if pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Not a PDF file")

    async def generate():
        text = extract_text(pdf_path)
        chunks = chunk_text(text)
        for chunk in chunks:
            try:
                audio = await synthesize_chunk(chunk)
                yield audio
            except Exception as exc:
                print(f"TTS error skipping chunk: {exc}")

    return StreamingResponse(generate(), media_type="audio/mpeg")
