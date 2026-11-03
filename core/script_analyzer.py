"""Rule-based lesson text cleanup and segmentation. No network or AI API calls."""
import re

def clean_notes(notes: str) -> str:
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError("Lesson notes must be a non-empty string.")
    text = notes.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def sentence_chunks(notes: str, max_sentences: int = 3):
    """Group sentences into readable chunks, preserving paragraph boundaries."""
    text = clean_notes(notes)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        sentences = [s.strip() for s in sentences if s.strip()]
        for start in range(0, len(sentences), max_sentences):
            chunks.append(" ".join(sentences[start:start + max_sentences]))
    return chunks or [text]
