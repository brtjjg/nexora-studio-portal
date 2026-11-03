"""Generates original educational scene cards locally using Pillow."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap

WIDTH, HEIGHT = 1280, 720

def _font(size, bold=False):
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()

class GraphicsEngine:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width, self.height = width, height

    def render_scene(self, scene, output_path):
        image = Image.new("RGB", (self.width, self.height), (13, 23, 42))
        draw = ImageDraw.Draw(image)
        # Decorative geometric system, generated locally.
        draw.ellipse((930, -180, 1450, 340), fill=(24, 65, 105))
        draw.ellipse((1030, 430, 1450, 850), fill=(20, 48, 78))
        draw.rounded_rectangle((70, 70, self.width - 70, self.height - 70),
                               radius=28, outline=(54, 104, 145), width=3)
        draw.text((110, 105), "NEXORA STUDIO  /  LESSON", font=_font(24, True), fill=(105, 205, 255))
        title = scene.get("title", "Lesson")
        draw.multiline_text((110, 185), "\n".join(textwrap.wrap(title, 34)[:2]),
                            font=_font(46, True), fill=(255, 255, 255), spacing=12)
        body = scene.get("narration", "")
        lines = textwrap.wrap(body, width=62)
        draw.multiline_text((115, 330), "\n".join(lines[:7]), font=_font(28),
                            fill=(220, 232, 244), spacing=17)
        draw.rounded_rectangle((110, 590, 380, 598), radius=4, fill=(56, 189, 248))
        draw.text((110, 625), f"SCENE {scene['scene_number']:02d}", font=_font(18, True), fill=(150, 175, 200))
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        return str(output_path)
