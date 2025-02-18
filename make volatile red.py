import os
from PIL import Image

def apply_red_hue(image_path):
    image = Image.open(image_path).convert("RGBA")

    # Get image data
    pixels = image.load()

    # Apply red filter
    for y in range(image.height):
        for x in range(image.width):
            if pixels is not None:
                r, g, b, a = pixels[x, y]
                pixels[x, y] = (min(255, int(r*1.15)), int(g*(4/5)), int(b*(4/5)), a)  # Reduce green & blue to enhance red
    return image

def process_images(folder_path):
    for filename in os.listdir(folder_path):
        if filename.startswith("non_red Energy") and filename.endswith("volatile.png"):
            image_path = os.path.join(folder_path, filename)
            red_image = apply_red_hue(image_path)
            new_filename = filename[8:]
            red_image.save(os.path.join(folder_path, new_filename))

if __name__ == "__main__":
    assets_folder = "assets"
    process_images(assets_folder)