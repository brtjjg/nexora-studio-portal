import uuid
from core.job_manager import JobManager
from engines.script_engine import ScriptEngine # Import the new engine

class ProductionCore:
    def __init__(self, db_connection):
        self.db = db_connection
        self.job_manager = JobManager(db_connection)
        self.script_engine = ScriptEngine(db_connection) # Initialize it

    def receive_lesson(self, lesson_id, title, notes):
        print(f"🧠 [Production Core] Received new project: {title}")
        project_id = str(uuid.uuid4())

        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO studio_projects (id, title, source_type, source_id, status)
            VALUES (%s, %s, 'academy_lesson', %s, 'planning')
        """, (project_id, title, lesson_id))
        self.db.commit()

        # Trigger the Script Engine directly with the notes
        self.script_engine.process_lesson(project_id, notes)
        
        return project_id
