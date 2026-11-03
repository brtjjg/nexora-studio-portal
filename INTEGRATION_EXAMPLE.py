"""Example only: adapt this pattern to your existing Flask route and job system."""
from core.production_brain import ProductionBrain

def generate_lesson_video(payload):
    required = ("lesson_id", "title", "notes")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError("Missing lesson fields: " + ", ".join(missing))

    brain = ProductionBrain(output_root="output")
    return brain.produce(
        lesson_id=payload["lesson_id"],
        title=payload["title"],
        notes=payload["notes"],
    )
