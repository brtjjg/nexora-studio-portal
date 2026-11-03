# Nexora Studio Production Brain

A self-hosted, deterministic video-production pipeline. It turns lesson notes into an educational MP4 using locally executed Python rules, Pillow graphics, offline speech synthesis and FFmpeg. **No external AI APIs or cloud-generation services are called.**

## Current pipeline

1. Validate lesson title and notes.
2. Split notes into scenes using deterministic sentence and paragraph rules.
3. Draw original 1280×720 scene graphics with Pillow.
4. Generate narration locally with `espeak-ng` (or local `pyttsx3`).
5. Read actual WAV duration so narration is not cut off by an estimated scene length.
6. Generate scene-level SRT subtitles.
7. Render and concatenate MP4 scenes with FFmpeg.
8. Save a JSON manifest and mark the project ready for admin review.

This is a working rule-based production MVP, not a semantic LLM or cinematic generator. It does not invent lesson facts; it organizes the supplied notes into visual scenes.

## Requirements

- Python 3.10+
- FFmpeg
- espeak-ng (recommended offline voice engine)
- Python packages in `requirements.txt`

On Debian/Ubuntu install system tools with:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg espeak-ng fonts-dejavu-core
pip install -r requirements.txt
```

## Run a local sample

```bash
python run_production.py --title "Introduction to Computers" --notes-file sample_lesson.txt --output output
```

The MP4 and manifest are created under `output/<lesson-id>/`.

## Flask API

Set these environment variables:

- `DATABASE_URL`: PostgreSQL connection string (required for lesson intake).
- `STUDIO_OUTPUT_DIR`: persistent directory for media; defaults to `uploads/videos`.
- `PORT`: web process port; defaults to 5000.

Apply the schema to the Studio PostgreSQL database:

```bash
psql "$DATABASE_URL" -f database/schema.sql
```

Start the API:

```bash
python app.py
```

Health check: `GET /api/health`

Academy lesson intake: `POST /api/receive-lesson`

```json
{
  "lesson_id": "academy-lesson-123",
  "title": "Introduction to Computers",
  "notes": "A computer is an electronic device..."
}
```

The API returns a project ID after rendering. The result is marked ready for admin review; approval and publication remain a separate Academy/admin workflow. The generated file is served below `/uploads/videos/`.

## Deployment notes

- The Dockerfile installs FFmpeg and `espeak-ng` inside the container.
- Attach a persistent disk to the deployment and point `STUDIO_OUTPUT_DIR` to its mount path. Without persistent storage, generated videos may disappear when a container is replaced.
- Video rendering is CPU-intensive. For real usage, move production calls into a background worker/queue so the HTTP request does not remain open during a long render.
- Keep the API private or authenticate Academy-to-Studio requests before public production use. Do not expose an unauthenticated intake endpoint to the internet.
- Apply `database/schema.sql` before first use.

## Main folders

- `core/`: text analysis, scene planning, orchestration and production brain.
- `engines/`: local graphics, offline voice, subtitles and FFmpeg rendering.
- `database/`: PostgreSQL schema.
- `uploads/videos/`: generated media at runtime (not committed to source control).
