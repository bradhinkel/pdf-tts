import os
from dotenv import load_dotenv

load_dotenv()

AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY", "")
AZURE_TTS_REGION = os.getenv("AZURE_TTS_REGION", "eastus")
AZURE_TTS_VOICE = os.getenv("AZURE_TTS_VOICE", "en-US-AriaNeural")
PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", "/app/pdfs")
MAX_PDF_SIZE = int(os.getenv("MAX_PDF_SIZE", "100000000"))
