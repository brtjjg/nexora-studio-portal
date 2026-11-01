class JobManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def queue_job(self, project_id, engine_name):
        print(f"⚙️ [Job Manager] Queuing {engine_name} for project {project_id}")
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO studio_jobs (project_id, engine_name, status)
            VALUES (%s, %s, 'queued')
        """, (project_id, engine_name))
        self.db.commit()
        
        self.trigger_worker(project_id, engine_name)

    def trigger_worker(self, project_id, engine_name):
        print(f"🚀 [Worker] Picked up {engine_name} job for {project_id}")
        
        if engine_name == 'voice':
            # Import here to avoid circular imports
            from engines.voice_engine import VoiceEngine
            engine = VoiceEngine(self.db)
            engine.process_job(project_id)
            
        elif engine_name == 'graphics':
            # We will build this in the next phase!
            print("🎨 [Graphics Engine] Not built yet, skipping for now.")
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE studio_jobs SET status = 'done' 
                WHERE project_id = %s AND engine_name = 'graphics'
            """, (project_id,))
            self.db.commit()
