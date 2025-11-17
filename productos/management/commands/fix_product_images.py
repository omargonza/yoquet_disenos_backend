from django.core.management.base import BaseCommand
from productos.models import Producto
import re

CLOUDINARY_BASE = "https://res.cloudinary.com/dfkyxmjnx/image/upload/yoquet/productos/"
MEDIA_BASE = "/media/productos/"

class Command(BaseCommand):
    help = "Corrige automáticamente las URLs de imágenes rotas en productos"

    def handle(self, *args, **kwargs):

        productos = Producto.objects.all()
        total = productos.count()

        self.stdout.write(self.style.WARNING(f"Corrigiendo imágenes de {total} productos..."))

        for p in productos:

            img = p.imagen

            # Si está vacío → nada que hacer
            if not img:
                continue

            # Caso 1 → Ya es Cloudinary correcto
            if img.startswith("https://res.cloudinary.com"):
                continue

            # Caso 2 → URL rota generada por Django API
            if "/api/productos" in img:
                # extraer nombre final
                filename = img.split("/")[-1]
                new_url = CLOUDINARY_BASE + filename + ".webp"
                p.imagen = new_url
                p.save()
                continue

            # Caso 3 → URL local que apunta mal
            if "127.0.0.1" in img or "api/productos" in img:
                filename = img.split("/")[-1]
                p.imagen = MEDIA_BASE + filename
                p.save()
                continue

            # Caso 4 → String simple (nombre de archivo)
            if re.match(r"^[\w\-\_]+\.(jpg|jpeg|png|webp|svg)$", img):
                p.imagen = CLOUDINARY_BASE + img
                p.save()
                continue

        self.stdout.write(self.style.SUCCESS("✔ Corrección completa. Las imágenes ahora son válidas."))
