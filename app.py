from flask import Flask, request, jsonify, send_from_directory
import psycopg2
import os
from core.orchestrator import ProductionCore

app = Flask(__name__)

# Use the external database URL from your environment variables.
# If you are testing locally, it falls back to the default local string.
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/nexora_studio"
)

def get_db():
    """Establishes connection to the external database."""
    return psycopg2.connect(DATABASE_URL)

@app.route('/api/receive-lesson', methods=['POST'])
def receive_lesson():
    """Entry point for the Academy to send new lessons to the Studio."""
    data = request.json
    lesson_id = data.get('lesson_id')
    title = data.get('title')
    notes = data.get('notes')

    if not lesson_id or not title or not notes:
        return jsonify({"error": "Missing required fields: lesson_id, title, or notes"}), 400

    try:
        db = get_db()
        core = ProductionCore(db)
        
        # Trigger the Production Brain
        project_id = core.receive_lesson(lesson_id, title, notes)
        
        db.close()
        return jsonify({
            "success": True, 
            "project_id": project_id, 
            "message": "Production Core initiated."
        }), 200
        
    except Exception as e:
        print(f"❌ [API Error] {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_uploads(filename):
    """
    Serves the generated audio, images, and final videos to the Vercel frontend.
    Example URL: https://nexora-studio-brain.onrender.com/uploads/videos/final.mp4
    """
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple endpoint for Render to check if the service is alive."""
    return jsonify({"status": "healthy", "service": "Nexora Studio Brain"}), 200

if __name__ == '__main__':
    os.makedirs(os.path.join(os.getcwd(), 'uploads'), exist_ok=True)
    
    # Render assigns a dynamic PORT. We must use it.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
