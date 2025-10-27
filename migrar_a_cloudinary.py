import os
import django
import cloudinary.uploader
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.base')
os.environ['DJANGO_DEBUG'] = 'True'

django.setup()

from productos.models import Producto

def subir_a_cloudinary_y_actualizar():
    productos = Producto.objects.all()
    total = productos.count()
    print(f"📦 Subiendo {total} productos a Cloudinary...")

    for i, producto in enumerate(productos, start=1):
        if not producto.imagen:
            print(f"❌ {i}/{total} | {producto.nombre} no tiene imagen, se salta.")
            continue

        ruta = producto.imagen.path
        if not os.path.exists(ruta):
            print(f"⚠️ {i}/{total} | Archivo no encontrado: {ruta}")
            continue

        try:
            res = cloudinary.uploader.upload(
                ruta,
                folder="yoquet/productos",
                overwrite=True,
                resource_type="image"
            )
            nueva_url = res["secure_url"]
            producto.imagen = nueva_url
            producto.save()
            print(f"✅ {i}/{total} | {producto.nombre} → {nueva_url}")
        except Exception as e:
            print(f"❌ Error subiendo {producto.nombre}: {e}")

    print("🎉 Migración completada correctamente.")

if __name__ == "__main__":
    subir_a_cloudinary_y_actualizar()
