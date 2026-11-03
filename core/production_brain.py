"""Orchestrates the first self-hosted Nexora Studio video pipeline."""
from pathlib import Path
from datetime import datetime, timezone
import json
import re

from .scene_planner import plan_scenes
from engines.graphics_engine import GraphicsEngine
from engines.voice_engine import VoiceEngine
from engines.subtitle_engine import SubtitleEngine
from engines.rendering_engine import RenderingEngine

class ProductionBrain:
    def __init__(self, output_root="output", voice_rate=155, voice=None):
        self.output_root = Path(output_root)
        self.graphics = GraphicsEngine()
        self.voice = VoiceEngine(rate=voice_rate, voice=voice)
        self.subtitles = SubtitleEngine()
        self.renderer = RenderingEngine()

    def produce(self, lesson_id, title, notes):
        safe_id = re.sub(r"[^A-Za-z0-9_-]+", "-", str(lesson_id)).strip("-") or "lesson"
        project = self.output_root / safe_id
        graphics_dir, audio_dir = project / "graphics", project / "audio"
        graphics_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)

        scenes = plan_scenes(title, notes)
        image_files, audio_files, durations = [], [], []
        for scene in scenes:
            number = scene["scene_number"]
            image_path = graphics_dir / f"scene_{number:03d}.png"
            audio_path = audio_dir / f"scene_{number:03d}.wav"
            self.graphics.render_scene(scene, image_path)
            self.voice.synthesize(scene["narration"], audio_path)
            image_files.append(str(image_path))
            audio_files.append(str(audio_path))
            durations.append(scene["duration_seconds"])

        srt_path = self.subtitles.write_srt(scenes, project / "subtitles.srt")
        video_path = self.renderer.render(
            image_files, audio_files, durations, srt_path, project / "final_video.mp4"
        )
        manifest = {
            "lesson_id": str(lesson_id),
            "title": title,
            "status": "awaiting_approval",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": "self_hosted_rule_based_v1",
            "scenes": scenes,
            "video_path": video_path,
            "subtitle_path": srt_path,
        }
        manifest_path = project / "production_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return {"status": "awaiting_approval", "video_path": video_path,
                "manifest_path": str(manifest_path), "scene_count": len(scenes)}
