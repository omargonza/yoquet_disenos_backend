import os
from django.core.management.base import BaseCommand
from django.db import transaction
from productos.models import Categoria, Producto
from cloudinary.uploader import upload as cloudinary_upload
from django.conf import settings
import mimetypes

mimetypes.init()
mimetypes.add_type("image/webp", ".webp", True)


class Command(BaseCommand):
    help = "Importación MASTER: escanea carpetas de categorías, crea productos y sube imágenes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            type=str,
            default=os.path.join(settings.MEDIA_ROOT, "productos"),
            help="Carpeta base de productos"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        base_folder = options["folder"]

        if not os.path.exists(base_folder):
            self.stderr.write(self.style.ERROR(f"❌ Carpeta no encontrada: {base_folder}"))
            return

        self.stdout.write(self.style.SUCCESS(f"🚀 Importando desde: {base_folder}"))

        total_cat = 0
        total_prod_new = 0
        total_prod_exist = 0

        for folder in os.listdir(base_folder):
            category_path = os.path.join(base_folder, folder)

            if not os.path.isdir(category_path):
                continue

            categoria, created = Categoria.objects.get_or_create(
                nombre=folder.capitalize()
            )
            if created:
                total_cat += 1
                self.stdout.write(self.style.SUCCESS(f"🆕 Categoría creada: {categoria.nombre}"))
            else:
                self.stdout.write(f"✔ Categoría existente: {categoria.nombre}")

            for filename in os.listdir(category_path):
                if not filename.lower().endswith(("jpg", "jpeg", "png", "webp")):
                    continue

                file_path = os.path.join(category_path, filename)
                nombre_base = os.path.splitext(filename)[0]
                nombre_limpio = nombre_base.replace("-", " ").replace("_", " ").capitalize()

                if Producto.objects.filter(nombre=nombre_limpio, categoria=categoria).exists():
                    self.stdout.write(f"↪ Ya existe: {nombre_limpio}")
                    total_prod_exist += 1
                    continue

                self.stdout.write(f"⬆ Subiendo imagen: {filename}")
                cloud_res = cloudinary_upload(
                    file_path,
                    folder=f"yoquet/productos/{folder}",
                    resource_type="image"
                )

                Producto.objects.create(
                    categoria=categoria,
                    nombre=nombre_limpio,
                    descripcion="",
                    precio=0,
                    stock=0,
                    destacado=False,
                    imagen=cloud_res["secure_url"],
                )

                self.stdout.write(self.style.SUCCESS(f"🆕 Producto creado: {nombre_limpio}"))
                total_prod_new += 1

        self.stdout.write(self.style.SUCCESS("===================================="))
        self.stdout.write(self.style.SUCCESS(f"📁 Categorías nuevas: {total_cat}"))
        self.stdout.write(self.style.SUCCESS(f"📦 Productos creados: {total_prod_new}"))
        self.stdout.write(self.style.SUCCESS(f"🔁 Ya existentes: {total_prod_exist}"))
        self.stdout.write(self.style.SUCCESS("🔥 PROCESO COMPLETO"))
