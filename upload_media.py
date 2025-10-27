import os
import cloudinary.uploader

MEDIA_ROOT = "media/productos"

for root, dirs, files in os.walk(MEDIA_ROOT):
    for file in files:
        path = os.path.join(root, file)
        cloudinary.uploader.upload(path, folder="yoquet/productos")
        print("✔ Subido:", path)
