"""Connects Academy lesson submissions to the local Nexora production pipeline."""
import uuid
from pathlib import Path
from core.production_brain import ProductionBrain


class ProductionCore:
    def __init__(self, db_connection, output_root="uploads/videos"):
        self.db = db_connection
        self.output_root = Path(output_root)

    def receive_lesson(self, lesson_id, title, notes):
        if not all(isinstance(value, str) and value.strip() for value in (str(lesson_id), title, notes)):
            raise ValueError("lesson_id, title and notes are required")
        project_id = str(uuid.uuid4())
        cursor = self.db.cursor()
        try:
            cursor.execute("""INSERT INTO studio_projects
                (id, title, source_type, source_id, status)
                VALUES (%s, %s, 'academy_lesson', %s, 'rendering')""",
                (project_id, title.strip(), str(lesson_id)))
            self.db.commit()
            result = ProductionBrain(output_root=self.output_root).produce(
                lesson_id=project_id, title=title.strip(), notes=notes)
            cursor.execute("""UPDATE studio_projects
                SET status='ready', video_path=%s, manifest_path=%s
                WHERE id=%s""", (f"/uploads/videos/{project_id}/final_video.mp4",
                 f"/uploads/videos/{project_id}/production_manifest.json", project_id))
            self.db.commit()
            return project_id
        except Exception as exc:
            self.db.rollback()
            try:
                cursor.execute("UPDATE studio_projects SET status='failed', error_log=%s WHERE id=%s",
                               (str(exc)[:4000], project_id))
                self.db.commit()
            except Exception:
                self.db.rollback()
            raise
        finally:
            cursor.close()
