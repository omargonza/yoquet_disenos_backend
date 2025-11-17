# productos/management/commands/fix_images.py
from django.core.management.base import BaseCommand
from productos.models import Producto

CLOUD_BASE = "https://res.cloudinary.com/dfkyxmjnx/image/upload/yoquet/"

class Command(BaseCommand):
    help = "Normaliza las imágenes para que tengan URLs correctas"

    def handle(self, *args, **kwargs):
        productos = Producto.objects.all()
        total = productos.count()
        self.stdout.write(f"🔍 Corrigiendo imágenes de {total} productos...\n")

        cambios = 0

        for p in productos:
            img = p.imagen

            if not img:
                continue

            # 👉 Si ya es URL completa, no tocar
            if img.startswith("http://") or img.startswith("https://"):
                continue

            # 👉 Si falta barra inicial, agregarla
            if not img.startswith("/"):
                img = "/" + img

            # 👉 Si parece Cloudinary pero sin dominio → agregar dominio
            if "image/upload" in img and not img.startswith("https://res.cloudinary.com"):
                new_url = CLOUD_BASE + img.lstrip("/")
                p.imagen = new_url
                p.save()
                cambios += 1
                continue

            # 👉 Si es media local
            if "/media/" not in img and "productos/" in img:
                new_url = CLOUD_BASE + img.lstrip("/")
                p.imagen = new_url
                p.save()
                cambios += 1
                continue

        self.stdout.write(f"\n✨ Listo. {cambios} imágenes fueron corregidas.\n")
