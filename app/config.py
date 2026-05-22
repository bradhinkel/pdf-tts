import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY", "")
AZURE_TTS_REGION = os.getenv("AZURE_TTS_REGION", "eastus")
AZURE_TTS_VOICE = os.getenv("AZURE_TTS_VOICE", "en-US-AriaNeural")
# Defaults to app/pdfs/ next to this file for local dev; override in .env for production
PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", str(Path(__file__).parent / "pdfs"))
MAX_PDF_SIZE = int(os.getenv("MAX_PDF_SIZE", "100000000"))

# Piper TTS
PIPER_VOICE = os.getenv("PIPER_VOICE", "en_US-lessac-medium")
PIPER_MODEL_DIR = os.getenv("PIPER_MODEL_DIR", str(Path(__file__).parent / "models" / "piper"))

# XTTS-v2
XTTS_SPEAKER = os.getenv("XTTS_SPEAKER", "Ana Florence")
