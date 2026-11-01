import uuid
from core.job_manager import JobManager

class ProductionCore:
    def __init__(self, db_connection):
        self.db = db_connection
        self.job_manager = JobManager(db_connection)

    def receive_lesson(self, lesson_id, title, notes):
        """Triggered when Academy sends a new lesson."""
        print(f"🧠 [Production Core] Received new project: {title}")
        
        project_id = str(uuid.uuid4())

        # 1. Create the Project in DB
        self.db.execute("""
            INSERT INTO studio_projects (id, title, source_type, source_id, status)
            VALUES (%s, %s, 'academy_lesson', %s, 'planning')
        """, (project_id, title, lesson_id))

        # 2. Send to Script Engine to break into scenes
        # (We will build this engine in Phase 2)
        self.job_manager.queue_job(project_id, 'script')
        
        return project_id

    def process_script_complete(self, project_id, scenes_data):
        """Called when the Script Engine finishes splitting the text."""
        print(f"🧠 [Production Core] Script ready. Queuing Audio & Graphics.")
        
        # Save scenes to DB
        for index, scene in enumerate(scenes_data):
            scene_id = str(uuid.uuid4())
            self.db.execute("""
                INSERT INTO studio_scenes (id, project_id, scene_order, narration_text, visual_prompt)
                VALUES (%s, %s, %s, %s, %s)
            """, (scene_id, project_id, index, scene['text'], scene['visual']))

        # 3. Queue the parallel engines
        self.job_manager.queue_job(project_id, 'voice')
        self.job_manager.queue_job(project_id, 'graphics')
