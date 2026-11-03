"""Writes scene-level SRT subtitles using known scene durations."""
from pathlib import Path

def _stamp(seconds):
    ms = int(round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"

class SubtitleEngine:
    def write_srt(self, scenes, output_path):
        cursor = 0.0
        blocks = []
        for index, scene in enumerate(scenes, start=1):
            duration = float(scene["duration_seconds"])
            start, end = cursor, cursor + duration
            text = scene["narration"].replace("\n", " ").strip()
            blocks.append(f"{index}\n{_stamp(start)} --> {_stamp(end)}\n{text}\n")
            cursor = end
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text("\n".join(blocks), encoding="utf-8")
        return str(output_path)
