import io
import json
import logging
import subprocess
import tarfile
import wave
from pathlib import Path
from urllib.request import urlretrieve

from app.config import PIPER_MODEL_DIR, PIPER_VOICE

logger = logging.getLogger(__name__)

# Piper standalone binary — no Python version constraints
_PIPER_RELEASE = "2023.11.14-2"
_PIPER_URL = (
    f"https://github.com/rhasspy/piper/releases/download"
    f"/{_PIPER_RELEASE}/piper_linux_x86_64.tar.gz"
)
_HF_BASE = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main"
    "/en/en_US/lessac/medium"
)


def _model_dir() -> Path:
    path = Path(PIPER_MODEL_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _piper_bin() -> Path:
    bin_path = _model_dir() / "piper" / "piper"
    if not bin_path.exists():
        archive = _model_dir() / "piper_linux_x86_64.tar.gz"
        logger.info("Downloading Piper binary...")
        urlretrieve(_PIPER_URL, archive)
        with tarfile.open(archive) as tar:
            tar.extractall(_model_dir())
        archive.unlink()
        bin_path.chmod(0o755)
        logger.info("Piper binary ready at %s", bin_path)
    return bin_path


def _ensure_model() -> tuple[Path, int]:
    model_dir = _model_dir()
    onnx = model_dir / f"{PIPER_VOICE}.onnx"
    config = model_dir / f"{PIPER_VOICE}.onnx.json"

    if not onnx.exists():
        logger.info("Downloading Piper voice model (~65 MB)...")
        urlretrieve(f"{_HF_BASE}/{PIPER_VOICE}.onnx", onnx)
        urlretrieve(f"{_HF_BASE}/{PIPER_VOICE}.onnx.json", config)
        logger.info("Piper model ready.")

    sample_rate = json.loads(config.read_text())["audio"]["sample_rate"]
    return onnx, sample_rate


def synthesize_all(chunks: list[str]) -> bytes:
    """Synthesize all chunks via piper binary, return a single PCM_16 WAV."""
    piper = _piper_bin()
    onnx, sample_rate = _ensure_model()

    all_raw = bytearray()
    for i, chunk in enumerate(chunks, 1):
        logger.info("Piper chunk %d/%d", i, len(chunks))
        result = subprocess.run(
            [str(piper), "--model", str(onnx), "--output-raw", "--quiet"],
            input=chunk.encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            logger.warning("Piper error on chunk %d: %s", i, result.stderr.decode())
            continue
        all_raw.extend(result.stdout)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(all_raw))
    buf.seek(0)
    return buf.read()
