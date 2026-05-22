import io
import logging
import wave
from pathlib import Path
from urllib.request import urlretrieve

from app.config import PIPER_MODEL_DIR, PIPER_VOICE

logger = logging.getLogger(__name__)

_HF_BASE = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main"
    "/en/en_US/lessac/medium"
)

_voice = None


def _ensure_model() -> Path:
    model_dir = Path(PIPER_MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    onnx = model_dir / f"{PIPER_VOICE}.onnx"
    json = model_dir / f"{PIPER_VOICE}.onnx.json"

    if not onnx.exists():
        logger.info("Downloading Piper voice model (~65 MB)...")
        urlretrieve(f"{_HF_BASE}/{PIPER_VOICE}.onnx", onnx)
        urlretrieve(f"{_HF_BASE}/{PIPER_VOICE}.onnx.json", json)
        logger.info("Piper model ready at %s", onnx)

    return onnx


def _load_voice():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        onnx = _ensure_model()
        logger.info("Loading Piper voice...")
        _voice = PiperVoice.load(str(onnx))
        logger.info("Piper voice loaded (sample_rate=%d)", _voice.config.sample_rate)
    return _voice


def synthesize_all(chunks: list[str]) -> bytes:
    """Synthesize all chunks and return a single PCM_16 WAV."""
    voice = _load_voice()
    raw_frames = b"".join(
        b"".join(voice.synthesize_stream_raw(chunk)) for chunk in chunks
    )

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(voice.config.sample_rate)
        wf.writeframes(raw_frames)
    buf.seek(0)
    return buf.read()
