import io
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from common.constants import (
    AVATAR_DEFAULT_SIZE,
    AVATAR_FILENAME,
    AVATAR_FONT_SCALE,
    AVATAR_FORMAT,
    AVATAR_TEXT_OFFSET_Y,
    FONTS,
    PASTEL_COLORS,
)


def pick_bg_color():
    return random.choice(PASTEL_COLORS)


def pick_text_color(bg_hex):
    bg = bg_hex.lstrip('#')
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    return '#222' if luminance > 180 else '#fff'


def generate_avatar(letter, size=AVATAR_DEFAULT_SIZE):
    bg_color = pick_bg_color()
    text_color = pick_text_color(bg_color)
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    font = None
    for font_name in FONTS:
        try:
            font = ImageFont.truetype(font_name, int(size * AVATAR_FONT_SCALE))
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_pos = ((size - w) / 2, (size - h) / 2 + AVATAR_TEXT_OFFSET_Y)
    draw.text(text_pos, letter, font=font, fill=text_color)
    buf = io.BytesIO()
    img.save(buf, format=AVATAR_FORMAT)
    return ContentFile(buf.getvalue(), name=AVATAR_FILENAME)
