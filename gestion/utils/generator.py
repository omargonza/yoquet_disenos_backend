import os
import hashlib
from cloudinary.uploader import upload
from productos.models import Producto, Categoria
from django.db import transaction


class ProductGenerator:
    """
    Genera productos completos leyendo carpetas:
    media/productos/<categoria>/
    Evita duplicados locales y Cloudinary usando hash MD5.
    """

    def _hash_file(self, ruta):
        md5 = hashlib.md5()
        with open(ruta, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _formatear_nombre(self, categoria, archivo):
        base = os.path.splitext(archivo)[0]
        base = base.replace("-", " ").replace("_", " ")
        base = base.title()
        return f"{categoria.title()} — {base}"

    def generar_desde_media(self, items):
        productos_creados = []

        hashes_existentes = set(
            Producto.objects.exclude(hash_imagen__isnull=True)
            .values_list("hash_imagen", flat=True)
        )

        with transaction.atomic():
            for item in items:

                ruta = item["ruta"]
                archivo = item["archivo"]
                categoria_nom = item["categoria"]

                hash_local = self._hash_file(ruta)

                # Evitar duplicados reales
                if hash_local in hashes_existentes:
                    print(f"[SKIP] Duplicado: {archivo}")
                    continue

                # Crear categoría si no existe
                categoria, _ = Categoria.objects.get_or_create(
                    nombre=categoria_nom.title()
                )

                # Subir a Cloudinary dentro de la carpeta por categoría
                try:
                    resultado = upload(
                        ruta,
                        folder=f"yoquet/productos/{categoria_nom}",
                        overwrite=False,
                    )
                except Exception as e:
                    print(f"[ERROR] Falló subida de {archivo}: {e}")
                    continue

                # Crear nombre formato profesional
                nombre = self._formatear_nombre(categoria_nom, archivo)

                # Crear producto
                p = Producto.objects.create(
                    categoria=categoria,
                    nombre=nombre,
                    descripcion="",
                    precio=0,
                    imagen=resultado["public_id"],
                    hash_imagen=hash_local,
                )

                productos_creados.append(p)
                hashes_existentes.add(hash_local)

        return productos_creados
