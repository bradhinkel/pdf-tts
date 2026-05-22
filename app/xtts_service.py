import asyncio
import io
import logging

logger = logging.getLogger(__name__)

_model = None  # underlying Xtts model


def _load_model():
    global _model
    if _model is None:
        import torch
        use_gpu = torch.cuda.is_available()
        logger.info("Loading XTTS-v2 (gpu=%s) — first run downloads ~1.8 GB...", use_gpu)

        # Use the TTS wrapper only for auto-download and checkpoint location,
        # then grab the underlying Xtts model to avoid the 'multi-speaker'
        # KeyError bug in TTS 0.22.0's wrapper .tts() method.
        from TTS.api import TTS
        wrapper = TTS("tts_models/multilingual/multi-speaker/xtts_v2", gpu=use_gpu)
        _model = wrapper.synthesizer.tts_model

        speakers = list(_model.speaker_manager.speakers.keys())
        logger.info("XTTS-v2 ready. %d speakers, e.g.: %s", len(speakers), speakers[:3])
    return _model


def _synthesize_sync(chunks: list[str], speaker: str) -> bytes:
    import numpy as np
    import soundfile as sf

    model = _load_model()

    # Fall back to first available speaker if the requested one isn't found
    available = list(model.speaker_manager.speakers.keys())
    if speaker not in available:
        logger.warning("Speaker '%s' not found, using '%s'", speaker, available[0])
        speaker = available[0]

    gpt_cond_latent = model.speaker_manager.speakers[speaker]["gpt_cond_latent"]
    speaker_embedding = model.speaker_manager.speakers[speaker]["speaker_embedding"]

    all_samples: list[float] = []
    for i, chunk in enumerate(chunks, 1):
        logger.info("XTTS chunk %d/%d", i, len(chunks))
        outputs = model.inference(
            text=chunk,
            language="en",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
        )
        wav = outputs["wav"]
        try:
            all_samples.extend(wav.tolist())
        except AttributeError:
            all_samples.extend(wav)

    buf = io.BytesIO()
    sf.write(buf, np.array(all_samples, dtype=np.float32), samplerate=24000, format="WAV")
    buf.seek(0)
    return buf.read()


async def synthesize_all(chunks: list[str], speaker: str = "Ana Florence") -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _synthesize_sync, chunks, speaker)
