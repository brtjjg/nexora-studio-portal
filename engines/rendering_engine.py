import os
import subprocess
import uuid

class RenderingEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        self.output_dir = os.path.join(os.getcwd(), 'uploads', 'videos')
        os.makedirs(self.output_dir, exist_ok=True)
        self.temp_dir = os.path.join(os.getcwd(), 'temp_render')
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_job(self, project_id):
        print(f"🎬 [Rendering Engine] Starting final video render for project {project_id}...")
        
        cursor = self.db.cursor()
        # Get all scenes ordered by scene_order
        cursor.execute("""
            SELECT id, audio_url, image_url FROM studio_scenes 
            WHERE project_id = %s ORDER BY scene_order ASC
        """, (project_id,))
        scenes = cursor.fetchall()

        if not scenes:
            print("❌ [Rendering Engine] No scenes found.")
            return

        scene_video_paths = []

        # 1. Render each scene individually
        for index, scene in enumerate(scenes):
            scene_id, audio_url, image_url = scene
            
            if not audio_url or not image_url:
                print(f"⚠️ [Rendering Engine] Missing audio or image for scene {scene_id}. Skipping.")
                continue

            scene_output = os.path.join(self.temp_dir, f"scene_{index}.mp4")
            audio_path = os.path.join(os.getcwd(), audio_url)
            image_path = os.path.join(os.getcwd(), image_url)

            print(f"   -> Rendering Scene {index + 1}...")
            
            # FFmpeg command: Loop image, attach audio, output mp4
            command = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', image_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                scene_output
            ]
            
            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                scene_video_paths.append(scene_output)
            except subprocess.CalledProcessError as e:
                print(f"❌ [Rendering Engine] FFmpeg failed on scene {index+1}: {e}")

        if not scene_video_paths:
            print("❌ [Rendering Engine] No scene videos were generated.")
            return

        # 2. Concatenate all scenes into one final video
        print("🎬 [Rendering Engine] Stitching all scenes together...")
        concat_file = os.path.join(self.temp_dir, 'concat_list.txt')
        with open(concat_file, 'w') as f:
            for video_path in scene_video_paths:
                f.write(f"file '{video_path}'\n")

        final_filename = f"{project_id}.mp4"
        final_video_path = os.path.join(self.output_dir, final_filename)

        concat_command = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            final_video_path
        ]

        try:
            subprocess.run(concat_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ [Rendering Engine] Final video created: {final_video_path}")
            
            # 3. Update the studio_productions table (This is what the Vercel Studio Portal reads!)
            video_url = f"/uploads/videos/{final_filename}"
            
            # We insert into the productions table so the Vercel dashboard sees it
            cursor.execute("""
                INSERT INTO studio_productions (lesson_id, title, status, video_url)
                SELECT source_id, title, 'ready', %s FROM studio_projects WHERE id = %s
            """, (video_url, project_id))
            
            # Update project status
            cursor.execute("UPDATE studio_projects SET status = 'completed' WHERE id = %s", (project_id,))
            self.db.commit()

        except subprocess.CalledProcessError as e:
            print(f"❌ [Rendering Engine] Failed to stitch video: {e}")

        # 4. Cleanup temporary scene files
        for temp_video in scene_video_paths:
            os.remove(temp_video)
        os.remove(concat_file)
        
        print("🧹 [Rendering Engine] Cleanup complete.")
