import asyncio
import io
import logging

logger = logging.getLogger(__name__)

_model = None


def _load_model():
    global _model
    if _model is None:
        logger.info("Loading XTTS-v2 model — first run takes ~1 min...")
        from TTS.api import TTS
        _model = TTS("tts_models/multilingual/multi-speaker/xtts_v2", gpu=False)
        logger.info("XTTS-v2 model ready.")
    return _model


def _synthesize_sync(chunks: list[str], speaker: str) -> bytes:
    import numpy as np
    import soundfile as sf

    model = _load_model()
    samples: list[float] = []

    for i, chunk in enumerate(chunks, 1):
        logger.info("XTTS chunk %d/%d", i, len(chunks))
        wav = model.tts(text=chunk, speaker=speaker, language="en")
        samples.extend(wav)

    buf = io.BytesIO()
    sf.write(buf, np.array(samples, dtype=np.float32), samplerate=24000, format="WAV")
    buf.seek(0)
    return buf.read()


async def synthesize_all(chunks: list[str], speaker: str = "Ana Florence") -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _synthesize_sync, chunks, speaker)
