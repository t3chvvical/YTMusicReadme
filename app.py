import os
import base64
import requests
import svgwrite
from flask import Flask, send_file
from ytmusicapi import YTMusic, OAuthCredentials
from src import constants

app = Flask(__name__)

client_id = constants.client_id
client_secret = constants.client_secret

ytmusic = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=client_id, client_secret=client_secret))

# Ruta de la carpeta donde se guardarán las imágenes SVG generadas
image_folder = 'static/images'

# Creo la carpeta
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Convierte la imagen a binario
def image_to_base64(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    return None

# Función para dividir el texto en múltiples líneas si es necesario
def wrap_text(text, max_width, font_size):
    lines = []
    words = text.split()
    current_line = words[0]
    
    for word in words[1:]:
        if len(current_line + ' ' + word) * font_size <= max_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

@app.route('/')
def get_latest_watch():
    history = ytmusic.get_history()  # Consigo el historial entero
    last_watched = history[0]
    title = last_watched['title']
    thumbnail_url = last_watched['thumbnails'][0]['url']

    # Descargo la imagen y la convierto a base64
    base64_image = image_to_base64(thumbnail_url)
    if base64_image is None:
        return "Error al obtener la imagen", 500

    # Creo el archivo
    svg_filename = f"image_{last_watched['videoId']}.svg"
    svg_path = os.path.join(image_folder, svg_filename)

    # Crea el dibujo SVG con un fondo blanco
    dwg = svgwrite.Drawing(svg_path, profile='tiny', size=(400, 300))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="white"))

    # Ajusto el texto y lo centro
    wrapped_title = wrap_text(title, constants.max_width, constants.font_size)
    y_position = 30
    for line in wrapped_title:
        dwg.add(dwg.text(line, insert=(200, y_position), font_size=constants.font_size, fill='black', text_anchor="middle"))
        y_position += constants.font_size + 5 # Espacio entre líneas

    # Centro la imagen
    image_x = (400 - 100) / 2 # 400 es el ancho total del SVG, 100 es el ancho de la imagen
    dwg.add(dwg.image(f"data:image/png;base64,{base64_image}", insert=(image_x, y_position), size=(100, 100)))

    # Guardo el fichero y lo devuelvo
    dwg.save()
    return send_file(svg_path, mimetype='image/svg+xml')
