import re

class ScriptEngine:
    def __init__(self, db_connection):
        self.db = db_connection

    def process_lesson(self, project_id, raw_notes):
        print(f"📝 [Script Engine] Analyzing lesson notes for project {project_id}...")
        
        # 1. Clean the text (remove extra spaces)
        text = re.sub(r'\s+', ' ', raw_notes).strip()
        
        # 2. Split into sentences based on punctuation (. ! ?)
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        # 3. Group sentences into chunks (scenes). 
        # Let's aim for roughly 2 sentences per scene.
        scenes = []
        current_chunk = ""
        
        for sentence in sentences:
            current_chunk += sentence + " "
            
            # If the chunk is long enough, save it as a scene
            if len(current_chunk) > 150:
                scenes.append(current_chunk.strip())
                current_chunk = ""
                
        # Catch any remaining text
        if current_chunk.strip():
            scenes.append(current_chunk.strip())

        # 4. Save scenes to the database
        cursor = self.db.cursor()
        for index, scene_text in enumerate(scenes):
            # Generate a visual prompt for the graphics engine based on the first few words
            visual_prompt = f"Educational diagram illustrating: {scene_text[:50]}..."
            
            cursor.execute("""
                INSERT INTO studio_scenes (project_id, scene_order, narration_text, visual_prompt, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """, (project_id, index + 1, scene_text, visual_prompt))
            
        self.db.commit()
        print(f"✅ [Script Engine] Successfully created {len(scenes)} scenes for project {project_id}.")

        # 5. Tell the Job Manager we are done with Scripting, and queue Audio
        self.queue_next_step(project_id)

    def queue_next_step(self, project_id):
        from core.job_manager import JobManager
        jm = JobManager(self.db)
        # Once script is done, we need Voice and Graphics
        jm.queue_job(project_id, 'voice')
        jm.queue_job(project_id, 'graphics')
