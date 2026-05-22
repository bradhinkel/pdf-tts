import re
from pathlib import Path

import pdfplumber


def extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = "\n\n".join(pages)
    # Collapse soft line breaks (single \n within a paragraph) into spaces
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Collapse runs of spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def chunk_text(text: str, min_words: int = 10, max_words: int = 200) -> list[str]:
    # Split on sentence-ending punctuation followed by whitespace and a capital letter
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)

    chunks: list[str] = []
    current: list[str] = []
    current_count = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        word_count = len(sentence.split())
        if current_count + word_count > max_words and current_count >= min_words:
            chunks.append(" ".join(current))
            current = [sentence]
            current_count = word_count
        else:
            current.append(sentence)
            current_count += word_count

    if current and current_count >= min_words:
        chunks.append(" ".join(current))

    return chunks
