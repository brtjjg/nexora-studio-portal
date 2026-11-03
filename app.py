"""Nexora Studio local production API. All content generation runs on this host."""
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import safe_join
import os
from pathlib import Path

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
DATABASE_URL = os.environ.get("DATABASE_URL")
UPLOADS_DIR = Path(os.environ.get("STUDIO_OUTPUT_DIR", "uploads/videos")).resolve()
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    import psycopg2
    return psycopg2.connect(DATABASE_URL)


@app.get('/api/health')
def health_check():
    return jsonify({"status": "healthy", "service": "Nexora Studio Brain",
                    "generation": "local_rule_based", "external_ai_apis": False})


@app.post('/api/receive-lesson')
def receive_lesson():
    data = request.get_json(silent=True) or {}
    lesson_id, title, notes = data.get('lesson_id'), data.get('title'), data.get('notes')
    if not all(isinstance(v, str) and v.strip() for v in (lesson_id, title, notes)):
        return jsonify({"error": "lesson_id, title and notes are required strings"}), 400
    db = None
    try:
        from core.orchestrator import ProductionCore
        db = get_db()
        project_id = ProductionCore(db, output_root=UPLOADS_DIR).receive_lesson(
            lesson_id.strip(), title.strip(), notes.strip())
        return jsonify({"success": True, "project_id": project_id,
                        "status": "ready_for_review",
                        "message": "Video rendered locally and is awaiting admin approval."}), 201
    except Exception as exc:
        app.logger.exception("Lesson production failed")
        return jsonify({"error": "Production failed", "detail": str(exc)}), 500
    finally:
        if db is not None:
            db.close()


@app.get('/uploads/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(UPLOADS_DIR, filename, as_attachment=False)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
