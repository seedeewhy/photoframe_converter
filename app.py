# flask run to start the server

# This is a simple Flask application that allows users to upload an image,
# crop it, and convert it to a specific format using a custom palette.
# The application uses the Pillow library for image processing and Flask for
# web serving. The uploaded images are saved in an 'uploads' directory, and
# the converted images are saved in an 'output' directory. The application
# also serves the converted images for download.
#

from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ACT_FILE = 'N-color.act'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_act_palette_image(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    if len(data) < 768:
        data += b'\x00' * (768 - len(data))
    palette_img = Image.new("P", (1, 1))
    palette_img.putpalette(list(data[:768]))
    return palette_img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    with Image.open(path) as img:
        width, height = img.size

    return {
        'filename': file.filename,
        'width': width,
        'height': height
    }


@app.route('/crop', methods=['POST'])
def crop():
    data = request.form
    filename = data['filename']
    x, y, w, h = map(int, [data['x'], data['y'], data['width'], data['height']])

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + '.bmp')

    with Image.open(input_path) as img:
        cropped = img.crop((x, y, x + w, y + h))

        # Rotate portrait crops to landscape orientation
        if h > w:
            cropped = cropped.rotate(-90, expand=True)

        # Resize to final landscape resolution
        resized = cropped.resize((800, 480))
        resized = resized.convert('RGB')

        palette_image = load_act_palette_image(ACT_FILE)
        quantized = resized.quantize(palette=palette_image, dither=Image.FLOYDSTEINBERG)
        quantized.save(output_path, format='BMP')

    return {'status': 'success', 'output': f'/output/{os.path.basename(output_path)}'}



@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)
