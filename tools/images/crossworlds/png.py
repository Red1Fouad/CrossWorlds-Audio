import os
from PIL import Image

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Loop through all files in the directory
for filename in os.listdir(script_dir):
    if filename.lower().endswith(".png"):
        png_path = os.path.join(script_dir, filename)
        png_path = os.path.splitext(png_path)[0] + ".png"

        # Open and convert the image
        with Image.open(png_path) as img:
            img.convert("RGBA").save(png_path, "PNG")

        print(f"Converted: {filename} -> {os.path.basename(png_path)}")

print("All .png files converted to .png!")
