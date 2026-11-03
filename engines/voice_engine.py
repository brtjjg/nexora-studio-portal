"""Offline speech synthesis. Prefers local espeak-ng; falls back to local pyttsx3."""
from pathlib import Path
import shutil
import subprocess

class VoiceEngine:
    def __init__(self, rate=155, voice=None):
        self.rate = rate
        self.voice = voice

    def synthesize(self, text, output_path):
        if not text.strip():
            raise ValueError("Cannot synthesize empty narration.")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        espeak = shutil.which("espeak-ng") or shutil.which("espeak")
        if espeak:
            command = [espeak, "-s", str(self.rate), "-w", str(output)]
            if self.voice:
                command += ["-v", self.voice]
            command.append(text)
            subprocess.run(command, check=True, capture_output=True, text=True)
            return str(output)

        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            if self.voice:
                voices = engine.getProperty("voices")
                match = next((v.id for v in voices if self.voice.lower() in
                              (v.id + " " + v.name).lower()), None)
                if match:
                    engine.setProperty("voice", match)
            engine.save_to_file(text, str(output))
            engine.runAndWait()
            engine.stop()
            if not output.exists() or output.stat().st_size == 0:
                raise RuntimeError("Local pyttsx3 engine did not create an audio file.")
            return str(output)
        except ImportError as exc:
            raise RuntimeError(
                "No offline speech engine found. Install espeak-ng on the host "
                "or install pyttsx3 and a local OS voice. No cloud voice API is used."
            ) from exc
