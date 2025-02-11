import os
import svgwrite
from flask import Flask, send_file
from ytmusicapi import YTMusic, OAuthCredentials
from src import constants

app = Flask(__name__)

client_id = constants.client_id
client_secret = constants.client_secret

ytmusic = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=client_id, client_secret=client_secret))
history = ytmusic.get_history() # Consigo el historial entero

# Ruta de la carpeta donde se guardarán las imágenes SVG generadas
image_folder = 'static/images'

# Creo la carpeta
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

@app.route('/')
def get_latest_watch():
    last_watched = history[0]
    title = last_watched['title']
    thumbnail_url = last_watched['thumbnails'][0]['url']

    # Creo el archivo
    svg_filename = f"image_{last_watched['videoId']}.svg"
    svg_path = os.path.join(image_folder, svg_filename)

    # Creo el SVG en sí y le agrego toda la pesca
    dwg = svgwrite.Drawing(svg_path, profile='tiny', size=(400, 200))
    dwg.add(dwg.text(title, insert=(20, 40), font_size=20, fill='black'))
    dwg.add(dwg.image(thumbnail_url, insert=(20, 60), size=(100, 100)))

    # Guardo el fichero y lo devuelvo
    dwg.save()
    return send_file(svg_path, mimetype='image/svg+xml')
