import asyncio
import io
import logging

logger = logging.getLogger(__name__)

_model = None  # underlying Xtts model


def _load_model():
    global _model
    if _model is None:
        import torch
        from TTS.api import TTS

        use_gpu = torch.cuda.is_available()
        device = "cuda" if use_gpu else "cpu"
        logger.info("Loading XTTS-v2 on %s...", device.upper())

        wrapper = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        _model = wrapper.synthesizer.tts_model.to(device)

        # Pin speaker embeddings to the same device
        for data in _model.speaker_manager.speakers.values():
            for k, v in data.items():
                if isinstance(v, torch.Tensor):
                    data[k] = v.to(device)

        speakers = list(_model.speaker_manager.speakers.keys())
        logger.info("XTTS-v2 ready. %d speakers, e.g.: %s", len(speakers), speakers[:3])
    return _model


def _split_for_xtts(text: str, max_chars: int = 200) -> list[str]:
    """Re-split a chunk into sub-chunks under XTTS's 250-char limit."""
    if len(text) <= max_chars:
        return [text]

    import re
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sub_chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if not current:
            current = sentence
        elif len(current) + 1 + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            sub_chunks.append(current)
            current = sentence

        # Hard-split any single sentence that's still too long
        while len(current) > max_chars:
            sub_chunks.append(current[:max_chars].rsplit(" ", 1)[0])
            current = current[len(sub_chunks[-1]):].strip()

    if current:
        sub_chunks.append(current)

    return sub_chunks or [text[:max_chars]]


def _synthesize_sync(chunks: list[str], speaker: str) -> bytes:
    import numpy as np
    import soundfile as sf

    model = _load_model()

    # Fall back to first available speaker if the requested one isn't found
    available = list(model.speaker_manager.speakers.keys())
    if speaker not in available:
        logger.warning("Speaker '%s' not found, using '%s'", speaker, available[0])
        speaker = available[0]

    device = next(model.parameters()).device
    gpt_cond_latent = model.speaker_manager.speakers[speaker]["gpt_cond_latent"].to(device)
    speaker_embedding = model.speaker_manager.speakers[speaker]["speaker_embedding"].to(device)

    # Expand chunks into XTTS-safe sub-chunks (<250 chars each)
    sub_chunks = [sc for chunk in chunks for sc in _split_for_xtts(chunk)]
    logger.info("XTTS: %d original chunks → %d sub-chunks", len(chunks), len(sub_chunks))

    all_samples: list[float] = []
    for i, chunk in enumerate(sub_chunks, 1):
        logger.info("XTTS sub-chunk %d/%d (%d chars)", i, len(sub_chunks), len(chunk))
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
    sf.write(buf, np.array(all_samples, dtype=np.float32), samplerate=24000,
             format="WAV", subtype="PCM_16")
    buf.seek(0)
    return buf.read()


async def synthesize_all(chunks: list[str], speaker: str = "Ana Florence") -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _synthesize_sync, chunks, speaker)
