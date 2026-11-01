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
        from engines.voice_engine import VoiceEngine
        engine = VoiceEngine(self.db)
        engine.process_job(project_id)
        
    elif engine_name == 'graphics':
        from engines.graphics_engine import GraphicsEngine
        engine = GraphicsEngine(self.db)
        engine.process_job(project_id)
        
    elif engine_name == 'render':
        from engines.rendering_engine import RenderingEngine
        engine = RenderingEngine(self.db)
        engine.process_job(project_id)
