import os
from django.core.management.base import BaseCommand, CommandError

# 🔧 Forzar carga de settings ANTES de importar nada
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.base")

import django
django.setup()

from django.conf import settings
from productos.models import Producto
import cloudinary.uploader
from tqdm import tqdm


class Command(BaseCommand):
    help = "Sincroniza imágenes locales con Cloudinary (sube, actualiza o crea según flags)."

    def add_arguments(self, parser):
        parser.add_argument("--prefix", type=str, default="yoquet/productos", help="Carpeta destino en Cloudinary.")
        parser.add_argument("--update-existing", action="store_true", help="Reemplaza imágenes ya subidas.")
        parser.add_argument("--create-missing", action="store_true", help="Sube imágenes que no existen en Cloudinary.")

    def handle(self, *args, **options):
        # 🧩 Verificar configuración de Cloudinary
        c = getattr(settings, "CLOUDINARY_STORAGE", {})
        cloud_name = c.get("CLOUD_NAME") or os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = c.get("API_KEY") or os.getenv("CLOUDINARY_API_KEY")
        api_secret = c.get("API_SECRET") or os.getenv("CLOUDINARY_API_SECRET")

        if not (cloud_name and api_key and api_secret):
            raise CommandError("Cloudinary no está configurado (faltan CLOUDINARY_*).")

        # ⚙️ Configurar Cloudinary manualmente
        import cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        # 🚀 Obtener productos
        productos = Producto.objects.exclude(imagen="")
        total = productos.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("⚠️ No hay productos con imágenes para sincronizar."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f"☁️ Sincronizando {total} productos con Cloudinary..."))

        prefix = options["prefix"]
        update_existing = options["update_existing"]
        create_missing = options["create_missing"]

        for p in tqdm(productos, desc="Subiendo imágenes"):
            if not p.imagen:
                continue

            # Saltar si ya tiene URL Cloudinary y no se pidió update
            if "res.cloudinary.com" in str(p.imagen) and not update_existing:
                continue

            # Obtener ruta local si existe
            path = getattr(p.imagen, "path", None)
            if not path or not os.path.exists(path):
                if create_missing:
                    self.stdout.write(self.style.WARNING(f"⚠️ {p.nombre}: no se encontró archivo local."))
                continue

            try:
                result = cloudinary.uploader.upload(
                    path,
                    folder=prefix,
                    public_id=os.path.splitext(os.path.basename(path))[0],
                    overwrite=update_existing,
                )
                p.imagen = result.get("secure_url")
                p.save()
                self.stdout.write(self.style.SUCCESS(f"✅ {p.nombre} → {p.imagen}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error al subir {p.nombre}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Sincronización completada correctamente."))
