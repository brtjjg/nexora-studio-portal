import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

class GraphicsEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        # Create an uploads/images folder if it doesn't exist
        self.output_dir = os.path.join(os.getcwd(), 'uploads', 'images')
        os.makedirs(self.output_dir, exist_ok=True)

    def process_job(self, project_id):
        print(f"🎨 [Graphics Engine] Starting visual generation for project {project_id}...")
        
        cursor = self.db.cursor()
        # Get all scenes for this project that need images
        cursor.execute("""
            SELECT id, narration_text, visual_prompt FROM studio_scenes 
            WHERE project_id = %s AND image_url IS NULL
        """, (project_id,))
        scenes = cursor.fetchall()

        if not scenes:
            print("⚠️ [Graphics Engine] No scenes found to generate images for.")
            return

        for scene in scenes:
            scene_id = scene[0]
            text = scene[1]
            visual_prompt = scene[2]
            
            filename = f"{scene_id}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            print(f"   -> Drawing graphics for Scene {scene_id[:8]}...")
            
            try:
                self._create_slide(text, visual_prompt, filepath)
                
                # Save the relative path to the database
                db_path = f"uploads/images/{filename}"
                cursor.execute("""
                    UPDATE studio_scenes SET image_url = %s WHERE id = %s
                """, (db_path, scene_id))
                self.db.commit()
            except Exception as e:
                print(f"❌ [Graphics Engine] Error drawing scene {scene_id}: {e}")

        print(f"✅ [Graphics Engine] Finished generating {len(scenes)} images.")
        
        # Mark job as done
        cursor.execute("""
            UPDATE studio_jobs SET status = 'done' 
            WHERE project_id = %s AND engine_name = 'graphics'
        """, (project_id,))
        self.db.commit()

    def _create_slide(self, text, prompt, output_path):
        """Generates a 1920x1080 educational slide using Pillow."""
        # 1. Setup Canvas (Dark Navy background to match your Academy branding)
        img = Image.new('RGB', (1920, 1080), color='#0B1F3A')
        draw = ImageDraw.Draw(img)
        
        # 2. Draw a decorative accent line on the left
        draw.rectangle([0, 0, 20, 1080], fill='#D4A63A') # Gold accent
        
        # 3. Load Fonts (Falls back to default if custom font isn't available)
        try:
            # If you upload a .ttf font to your repo, specify the path here
            # font_title = ImageFont.truetype("assets/fonts/Roboto-Bold.ttf", 60)
            # font_body = ImageFont.truetype("assets/fonts/Roboto-Regular.ttf", 45)
            font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 60) # Linux default
            font_body = ImageFont.truetype("DejaVuSans.ttf", 45)
        except IOError:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()

        # 4. Draw Visual Prompt (Small text at the top)
        draw.text((100, 100), prompt, font=font_title, fill='#29A9E8') # Blue accent
        
        # 5. Wrap and Draw Narration Text (Large text in the middle)
        wrapped_text = textwrap.fill(text, width=50)
        draw.text((100, 300), wrapped_text, font=font_body, fill='#FFFFFF', spacing=20)
        
        # 6. Save the image
        img.save(output_path)
