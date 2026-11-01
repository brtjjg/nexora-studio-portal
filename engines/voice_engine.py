import asyncio
import edge_tts
import os
import uuid

class VoiceEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        # Create an uploads/audio folder in Termux if it doesn't exist
        self.output_dir = os.path.join(os.getcwd(), 'uploads', 'audio')
        os.makedirs(self.output_dir, exist_ok=True)

    async def _generate_audio(self, text, filepath, voice):
        """Uses edge-tts to generate an audio file."""
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)

    def process_job(self, project_id):
        print(f"🎙️ [Voice Engine] Starting audio generation for project {project_id}...")
        
        cursor = self.db.cursor()
        # Get all scenes for this project that need audio
        cursor.execute("""
            SELECT id, narration_text FROM studio_scenes 
            WHERE project_id = %s AND audio_url IS NULL
        """, (project_id,))
        scenes = cursor.fetchall()

        if not scenes:
            print("⚠️ [Voice Engine] No scenes found to generate audio for.")
            return

        # Default voice (you can change this later to match the Studio UI dropdown)
        voice = "en-US-AriaNeural" 

        for scene in scenes:
            scene_id = scene[0]
            text = scene[1]
            
            # Generate a unique filename for the audio
            filename = f"{scene_id}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            print(f"   -> Generating voice for Scene {scene_id[:8]}...")
            
            # Run the async TTS function
            try:
                asyncio.run(self._generate_audio(text, filepath, voice))
                
                # Save the relative path to the database
                db_path = f"uploads/audio/{filename}"
                cursor.execute("""
                    UPDATE studio_scenes SET audio_url = %s WHERE id = %s
                """, (db_path, scene_id))
                self.db.commit()
            except Exception as e:
                print(f"❌ [Voice Engine] Error generating audio for scene {scene_id}: {e}")

        print(f"✅ [Voice Engine] Finished generating {len(scenes)} audio files.")
        
        # Mark job as done
        cursor.execute("""
            UPDATE studio_jobs SET status = 'done' 
            WHERE project_id = %s AND engine_name = 'voice'
        """, (project_id,))
        self.db.commit()
