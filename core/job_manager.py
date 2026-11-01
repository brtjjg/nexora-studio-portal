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
        
        self.trigger_worker(engine_name)

    def trigger_worker(self, engine_name):
        print(f"🚀 [Worker] Picked up {engine_name} job.")
