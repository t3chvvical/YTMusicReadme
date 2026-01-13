import os
import base64
import requests
import svgwrite
from flask import Flask, send_file
from ytmusicapi2 import YTMusic

from constants import (
    YT_CLIENT_CONFIG,
    IMAGE_FOLDER, SVG_FILENAME,
    SVG_WIDTH, SVG_HEIGHT,
    CARD_MARGIN, CARD_CORNER_RADIUS, CARD_FILL_COLOR, CARD_FILL_OPACITY,
    IMG_SIZE, IMG_CORNER_RADIUS, IMG_SHADOW_OFFSET, IMG_SHADOW_OPACITY, IMG_THRESHOLD, IMG_Y_POSITION,
    BG_GRADIENT_ID, BG_GRADIENT_START_COLOR, BG_GRADIENT_END_COLOR, GRADIENT_ANIMATION_DURATION,
    IMAGE_PULSE_FROM, IMAGE_PULSE_TO, IMAGE_PULSE_DURATION,
    TITLE_FONT_SIZE, TITLE_FONT_WEIGHT, TITLE_FONT_COLOR, TITLE_FONT_FAMILY,
    TITLE_MAX_CHARS, TITLE_MAX_LINES, TITLE_LINE_SPACING,
    ARTIST_FONT_SIZE, ARTIST_FONT_COLOR, ARTIST_FONT_FAMILY, ARTIST_Y_OFFSET
)

app = Flask(__name__)
ytmusic = YTMusic(YT_CLIENT_CONFIG)

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


def image_to_base64(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    return None


def wrap_text(text, max_chars_per_line=TITLE_MAX_CHARS, max_lines=TITLE_MAX_LINES):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        candidate = (current_line + " " + word).strip()
        if len(candidate) <= max_chars_per_line:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word
            if len(lines) >= max_lines:
                break

    if current_line and len(lines) < max_lines:
        lines.append(current_line)

    if len(words) > sum(len(l.split()) for l in lines):
        lines[-1] = lines[-1].rstrip('.') + "..."

    return lines


@app.route('/')
def get_latest_watch():
    last_watched = ytmusic.get_history()[0]
    title = last_watched['title']
    artists = (last_watched.get("artists") or [{"name": "Desconocido"}])[0]['name'].split(", ")[0]

    thumbnail_url = last_watched['thumbnails'][0]['url']
    base64_image = image_to_base64(thumbnail_url)
    if base64_image is None:
        return "Error al obtener la imagen", 500

    svg_path = os.path.join(IMAGE_FOLDER, SVG_FILENAME)
    dwg = svgwrite.Drawing(svg_path, profile='full', size=(f"{SVG_WIDTH}px", f"{SVG_HEIGHT}px"))

    # Fondo degradado animado
    gradient = dwg.linearGradient(start=(0, 0), end=(1, 1), id=BG_GRADIENT_ID)
    gradient.add_stop_color(0, BG_GRADIENT_START_COLOR)
    gradient.add_stop_color(1, BG_GRADIENT_END_COLOR)
    dwg.defs.add(gradient)

    gradient.add(svgwrite.animate.AnimateTransform(
        transform='translate',
        from_='0,0',
        to='1,1',
        dur=GRADIENT_ANIMATION_DURATION,
        repeatCount='indefinite'
    ))

    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill=f"url(#{BG_GRADIENT_ID})"))

    # Tarjeta
    dwg.add(dwg.rect(
        insert=(CARD_MARGIN, CARD_MARGIN),
        size=(SVG_WIDTH - 2 * CARD_MARGIN, SVG_HEIGHT - 2 * CARD_MARGIN),
        rx=CARD_CORNER_RADIUS, ry=CARD_CORNER_RADIUS,
        fill=CARD_FILL_COLOR, fill_opacity=CARD_FILL_OPACITY
    ))

    # Imagen
    img_x = SVG_WIDTH / 2 - IMG_SIZE / 2
    clip_id = "roundedClip"
    clip_path = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip_path.add(dwg.rect(insert=(img_x, IMG_Y_POSITION), size=(IMG_SIZE, IMG_SIZE), rx=IMG_CORNER_RADIUS, ry=IMG_CORNER_RADIUS))

    dwg.add(dwg.rect(
        insert=(img_x - IMG_SHADOW_OFFSET, IMG_Y_POSITION - IMG_SHADOW_OFFSET),
        size=(IMG_SIZE + 2 * IMG_SHADOW_OFFSET, IMG_SIZE + 2 * IMG_SHADOW_OFFSET),
        rx=IMG_CORNER_RADIUS, ry=IMG_CORNER_RADIUS,
        fill="black", fill_opacity=IMG_SHADOW_OPACITY
    ))

    image_element = dwg.image(
        f"data:image/png;base64,{base64_image}",
        insert=(img_x, IMG_Y_POSITION),
        size=(IMG_SIZE, IMG_SIZE),
        clip_path=f"url(#{clip_id})"
    )

    image_element.add(svgwrite.animate.AnimateTransform(
        transform='scale',
        from_=IMAGE_PULSE_FROM,
        to=IMAGE_PULSE_TO,
        dur=IMAGE_PULSE_DURATION,
        repeatCount='indefinite',
        additive='sum',
        fill='freeze'
    ))

    dwg.add(image_element)

    # Título
    y = IMG_Y_POSITION + IMG_SIZE + IMG_THRESHOLD
    for line in wrap_text(title):
        dwg.add(dwg.text(
            line,
            insert=(SVG_WIDTH / 2, y),
            text_anchor="middle",
            fill=TITLE_FONT_COLOR,
            font_size=TITLE_FONT_SIZE,
            font_weight=TITLE_FONT_WEIGHT,
            font_family=TITLE_FONT_FAMILY
        ))
        y += TITLE_LINE_SPACING

    # Artista
    dwg.add(dwg.text(
        artists,
        insert=(SVG_WIDTH / 2, y + ARTIST_Y_OFFSET),
        text_anchor="middle",
        fill=ARTIST_FONT_COLOR,
        font_size=ARTIST_FONT_SIZE,
        font_family=ARTIST_FONT_FAMILY
    ))

      dwg.save()
    return send_file(svg_path, mimetype='image/svg+xml')
