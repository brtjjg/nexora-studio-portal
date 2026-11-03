# Nexora Studio Production Brain v1

A self-hosted, API-free MVP pipeline that turns lesson notes into a narrated MP4 using local Python code, local graphics, local speech synthesis and FFmpeg.

## What it does

1. Accepts lesson title and notes.
2. Splits notes into scenes and creates narration text.
3. Generates original slide-style graphics with Pillow.
4. Generates narration using a local speech engine (`espeak-ng` or `pyttsx3`).
5. Creates subtitles (scene-level timing in this MVP).
6. Renders an MP4 with FFmpeg.
7. Writes a JSON production manifest.

No external AI APIs or cloud generation services are used. The script/scene logic is deterministic rule-based software, not a generative language model.

## Requirements

- Python 3.10+
- FFmpeg installed and available on PATH
- Pillow
- For offline voice, install either:
  - `espeak-ng` on the host machine (recommended), or
  - `pyttsx3` plus a local OS speech engine

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Check FFmpeg:

```bash
ffmpeg -version
```

Check local speech:
- Linux: `espeak-ng --version`
- Or install `pyttsx3` and ensure your operating system has an offline voice installed.

## Run

```bash
python run_production.py --title "Introduction to Computers" --notes-file sample_lesson.txt --output output
```

Or pass notes directly:

```bash
python run_production.py --title "Introduction to Computers" --notes "A computer is an electronic device..."
```

The MP4 and production manifest are saved under the output directory.

## Important production notes

- This is the first working foundation, not a cinematic AI video generator.
- Graphics are original programmatically drawn educational slides.
- Scene splitting is rules-based. It does not claim to understand complex subject matter like a large language model.
- Voice is generated locally. If no offline speech engine is installed, the voice stage fails clearly instead of silently producing a video without narration.
- Scene-level subtitles are synchronized to each scene's duration. Word-level karaoke timing is a later enhancement.
- The renderer uses FFmpeg as a local rendering utility.

## Integrating with the existing Flask app

Do not replace your current `app.py` blindly. Import `ProductionBrain` from this package and call it from a background worker after validating the Academy lesson payload.

Example:

```python
from core.production_brain import ProductionBrain

brain = ProductionBrain(output_root="output")
result = brain.produce(
    lesson_id="lesson-001",
    title="Introduction to Computers",
    notes="A computer is an electronic device..."
)
```

For production deployment, run jobs in a background worker process rather than inside a Flask request. Persist job status in your existing PostgreSQL database and keep generated media in durable storage.

## Directory layout

```text
core/
  production_brain.py
  script_analyzer.py
  scene_planner.py
  job_manager.py
engines/
  graphics_engine.py
  voice_engine.py
  subtitle_engine.py
  rendering_engine.py
run_production.py
```
