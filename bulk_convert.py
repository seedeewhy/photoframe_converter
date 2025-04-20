# bulk converts everything in input folder to BMP in output foloder
# note: it auto crops, you cannot define crop.
# for choosing crop, use the web app

from PIL import Image, ImageOps
import os

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
ACT_FILE = 'N-color.act'
SUPPORTED_EXTS = ('.jpg', '.jpeg', '.png', '.bmp')

def load_act_as_palette_image(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    # Pad to 768 bytes (256 colors × 3 bytes each)
    if len(data) < 768:
        data += b'\x00' * (768 - len(data))
    palette_img = Image.new("P", (1, 1))
    palette_img.putpalette(list(data[:768]))
    return palette_img

def crop_to_aspect(img, target_aspect):
    w, h = img.size
    current_aspect = w / h

    if current_aspect > target_aspect:
        # Too wide — crop width
        new_w = int(h * target_aspect)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_aspect < target_aspect:
        # Too tall — crop height
        new_h = int(w / target_aspect)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img

def crop_to_aspect(img, target_aspect):
    w, h = img.size
    current_aspect = w / h

    if current_aspect > target_aspect:
        # Too wide — crop width
        new_w = int(h * target_aspect)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_aspect < target_aspect:
        # Too tall — crop height
        new_h = int(w / target_aspect)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img

def convert_image(input_path, output_path, palette_image):
    with Image.open(input_path) as img:
        # Rotate if portrait
        if img.height > img.width:
            img = img.rotate(-90, expand=True)

        # Crop to target aspect ratio (800:480 = 5:3)
        img = crop_to_aspect(img, target_aspect=800/480)

        # Resize to display resolution
        img = img.resize((800, 480))
        img = img.convert("RGB")

        # Apply vendor color palette with Floyd–Steinberg dithering
        img = img.quantize(palette=palette_image, dither=Image.FLOYDSTEINBERG)
        img.save(output_path, format='BMP')


def batch_convert():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    palette_image = load_act_as_palette_image(ACT_FILE)

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(SUPPORTED_EXTS):
            input_path = os.path.join(INPUT_DIR, filename)
            output_filename = os.path.splitext(filename)[0] + '.bmp'
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            print(f"Converting {filename} -> {output_filename}")
            convert_image(input_path, output_path, palette_image)

if __name__ == "__main__":
    batch_convert()
