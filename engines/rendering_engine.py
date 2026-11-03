"""Local FFmpeg renderer: scene cards + offline narration + subtitles -> MP4."""
from pathlib import Path
import shutil
import subprocess

class RenderingEngine:
    def __init__(self, ffmpeg="ffmpeg"):
        self.ffmpeg = shutil.which(ffmpeg)

    def render(self, scene_images, audio_files, durations, subtitle_path, output_path):
        if not self.ffmpeg:
            raise RuntimeError("FFmpeg was not found on PATH. Install FFmpeg on the host.")
        if not scene_images or len(scene_images) != len(audio_files) or len(audio_files) != len(durations):
            raise ValueError("Scene images, audio files and durations must have matching non-zero lengths.")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        work = output.parent / "render_work"
        work.mkdir(parents=True, exist_ok=True)
        concat_file = work / "scenes.txt"
        # Build one still-video segment per scene, with its own narration audio.
        segments = []
        for i, (image, audio, duration) in enumerate(zip(scene_images, audio_files, durations)):
            segment = work / f"segment_{i:03d}.mp4"
            command = [
                self.ffmpeg, "-y", "-loop", "1", "-i", str(image), "-i", str(audio),
                "-t", str(float(duration)), "-r", "25",
                "-vf", "scale=1280:720,format=yuv420p",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k", "-shortest", str(segment)
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            segments.append(segment)

        concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments), encoding="utf-8")
        command = [
            self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-vf", f"subtitles={Path(subtitle_path).as_posix()}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        return str(output)
