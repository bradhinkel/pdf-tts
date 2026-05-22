import httpx

from app.config import AZURE_TTS_KEY, AZURE_TTS_REGION, AZURE_TTS_VOICE


def _tts_url() -> str:
    return f"https://{AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"


def _ssml(text: str, voice: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<speak version='1.0' xml:lang='en-US'>"
        f"<voice xml:lang='en-US' name='{voice}'>{text}</voice>"
        f"</speak>"
    )


async def synthesize_chunk(text: str) -> bytes:
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            _tts_url(),
            headers=headers,
            content=_ssml(text, AZURE_TTS_VOICE).encode("utf-8"),
        )
        response.raise_for_status()
        return response.content
