import os
import base64
import requests
import svgwrite
from flask import Flask, send_file
from ytmusicapi2 import YTMusic

app = Flask(__name__)

ytmusic = YTMusic('browser.json')
image_folder = '/tmp'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Convierte la imagen a binario
def image_to_base64(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    return None

# Función para dividir el texto en múltiples líneas si es necesario
def wrap_text(text, max_chars_per_line=18, max_lines=2):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line:
            current_line = (current_line + " " + word).strip()
        else:
            lines.append(current_line)
            current_line = word
        if len(lines) >= max_lines:
            break
    lines.append(current_line)

    # Si el texto se cortó, añadimos puntos suspensivos
    if len(words) > sum(len(l.split()) for l in lines):
        if len(lines) > 0:
            lines[-1] = lines[-1].rstrip(".") + "..."

    return lines[:max_lines]

# FIXME: Las animaciones parecen no funcionar :(
@app.route('/')
def get_latest_watch():
    history = ytmusic.get_history() # Consigo el historial entero
    last_watched = history[0]
    title = last_watched['title']
    thumbnail_url = last_watched['thumbnails'][0]['url']
    artists = last_watched.get("artists")[0]['name'] if last_watched.get("artists") else "Desconocido"

    # Descargo la imagen y la convierto a base64
    base64_image = image_to_base64(thumbnail_url)
    if base64_image is None:
        return "Error al obtener la imagen", 500

    svg_filename = "image.svg"
    svg_path = os.path.join(image_folder, svg_filename)

    width, height = 500, 350
    dwg = svgwrite.Drawing(svg_path, profile='full', size=(f"{width}px", f"{height}px"))

    # Fondo degradado
    gradient = dwg.linearGradient(start=(0, 0), end=(1, 1), id="bgGradient")
    gradient.add_stop_color(0, '#141E30')
    gradient.add_stop_color(1, '#243B55')
    dwg.defs.add(gradient)

    animate_grad = svgwrite.animate.AnimateTransform(
        transform='translate',
        from_='0,0',
        to='1,1',
        dur='10s',
        repeatCount='indefinite'
    )
    gradient.add(animate_grad)

    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill="url(#bgGradient)"))

    # Tarjeta central translúcida
    dwg.add(dwg.rect(
        insert=(20, 20),
        size=(width - 40, height - 40),
        rx=20, ry=20,
        fill="rgb(255,255,255)",
        fill_opacity=0.08
    ))

    # Imagen del álbum con recorte redondeado
    img_size = 120
    img_x = width / 2 - img_size / 2
    img_y = 80
    clip_id = "roundedClip"
    clip_path = dwg.defs.add(dwg.clipPath(id=clip_id))
    clip_path.add(dwg.rect(insert=(img_x, img_y), size=(img_size, img_size), rx=15, ry=15))

    # Sombra
    dwg.add(dwg.rect(
        insert=(img_x - 5, img_y - 5),
        size=(img_size + 10, img_size + 10),
        rx=20, ry=20,
        fill="rgb(0,0,0)",
        fill_opacity=0.3
    ))

    image_element = dwg.image(
        f"data:image/png;base64,{base64_image}",
        insert=(img_x, img_y),
        size=(img_size, img_size),
        clip_path=f"url(#{clip_id})"
    )

    pulse_anim = svgwrite.animate.AnimateTransform(
        transform='scale',
        from_='1',
        to='1.05',
        dur='3s',
        repeatCount='indefinite',
        additive='sum',
        fill='freeze'
    )
    image_element.add(pulse_anim)
    dwg.add(image_element)

    # Título
    wrapped_title = wrap_text(title, max_chars_per_line=20, max_lines=2)
    y_position = img_y + img_size + 40
    for line in wrapped_title:
        dwg.add(dwg.text(
            line,
            insert=(width / 2, y_position),
            text_anchor="middle",
            fill='white',
            font_size="22px",
            font_weight="bold",
            font_family="sans-serif"
        ))
        y_position += 26

    # Artista
    dwg.add(dwg.text(
        artists,
        insert=(width / 2, y_position + 10),
        text_anchor="middle",
        fill='#CCCCCC',
        font_size="16px",
        font_family="sans-serif"
    ))

    # Guardo el fichero y lo devuelvo
    dwg.save()
    return send_file(svg_path, mimetype='image/svg+xml')