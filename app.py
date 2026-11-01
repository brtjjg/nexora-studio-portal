from flask import Flask, request, jsonify
import psycopg2
from core.orchestrator import ProductionCore

app = Flask(__name__)

# Connecting to the LOCAL Termux database
def get_db():
    return psycopg2.connect(
        dbname="nexora_studio",
        user="postgres", 
        host="127.0.0.1", # Localhost
        port="5432"
    )

@app.route('/api/receive-lesson', methods=['POST'])
def receive_lesson():
    data = request.json
    lesson_id = data.get('lesson_id')
    title = data.get('title')
    notes = data.get('notes')

    db = get_db()
    core = ProductionCore(db)
    
    project_id = core.receive_lesson(lesson_id, title, notes)
    
    return jsonify({"success": True, "project_id": project_id, "message": "Production Core initiated."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
