"""Creates deterministic scene records from lesson text."""
from .script_analyzer import sentence_chunks

def plan_scenes(title: str, notes: str, max_sentences: int = 3):
    chunks = sentence_chunks(notes, max_sentences=max_sentences)
    scenes = []
    for index, chunk in enumerate(chunks, start=1):
        scenes.append({
            "scene_number": index,
            "title": f"{title} — Part {index}",
            "narration": chunk,
            "visual_type": "concept_card",
            "duration_seconds": max(6, min(22, round(len(chunk.split()) / 2.25))),
        })
    return scenes
