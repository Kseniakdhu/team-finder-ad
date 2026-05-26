import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

PASTEL_COLORS = [
    '#A3C1DA', '#B5D8B2', '#F7CAC9', '#F6E2B3', '#B7D7E8', '#E2C2B9',
    '#C3B1E1', '#F9E79F', '#AED9E0', '#F5CBA7', '#D5ECC2', '#E4BAD4',
    '#B8E0D2', '#F7D6E0', '#D6EAF8', '#F9E79F', '#D5F5E3', '#FAD7A0',
    '#D2B4DE', '#F6DDCC'
]


def pick_bg_color():
    return random.choice(PASTEL_COLORS)


def pick_text_color(bg_hex):
    bg = bg_hex.lstrip('#')
    r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
    luminance = (0.299*r + 0.587*g + 0.114*b)
    return '#222' if luminance > 180 else '#fff'


def generate_avatar(letter, size=128):
    bg_color = pick_bg_color()
    text_color = pick_text_color(bg_color)
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', int(size*0.6))
    except Exception:
        font = ImageFont.load_default()
    # Pillow >=10: use textbbox instead of textsize
    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size-w)/2, (size-h)/2-5), letter, font=font, fill=text_color)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name='avatar.png')
