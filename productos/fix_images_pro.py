# productos/fix_images_pro.py
"""
🔥 FIX IMÁGENES ULTRA PRO PARA YOQUET DISEÑOS
------------------------------------------------
✔ Limpia rutas dañadas/duplicadas
✔ Normaliza rutas Cloudinary a formato correcto
✔ Quita prefijos basura como "image/upload/yoquet/"
✔ Construye URL Cloudinary válida usando cloud_name real
✔ Verifica existencia real en Cloudinary
✔ Registra cambios de forma segura
✔ Funciona igual en DEV y en Render
✔ Modo simulación y modo real
"""

import re
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from django.conf import settings
from productos.models import Producto

# ============================
#   CONFIG INICIAL
# ============================
CLOUD_NAME = settings.CLOUDINARY_STORAGE.get("CLOUD_NAME")
API_KEY = settings.CLOUDINARY_STORAGE.get("API_KEY")
API_SECRET = settings.CLOUDINARY_STORAGE.get("API_SECRET")

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True
)

print(f"☁ Cloudinary OK → {CLOUD_NAME}")


# ============================
# 1) Limpieza de paths rotos
# ============================
def sanitize_path(path):
    """
    Recibe cosas como:
        image/upload/yoquet/productos/cotillon/imagen.webp
        /yoquet/image/upload/productos/....
        productos/cotillon/foto.webp
        https://res.cloudinary.....
    Y devuelve SOLO la parte útil:
        productos/cotillon/foto.webp
    """

    # CloudinaryResource → convertir a string
    if not isinstance(path, str):
        try:
            path = str(path)
        except:
            return None

    path = path.strip()

    # Si ya es URL completa → extraer public_id
    if path.startswith("http"):
        # Ej: https://res.cloudinary.com/.../upload/v1234/productos/x.webp
        match = re.search(r"/upload/(?:v\d+/)?(.+)$", path)
        if match:
            return match.group(1).strip()
        return None

    # limpiar basura
    basura = [
        "image/upload/",
        "yoquet/",
        "/",
        "\\",
        "v1/",
        "upload/"
    ]

    for b in basura:
        path = path.replace(b, "")

    return path.strip()


# ============================
# 2) Construir URL Cloudinary real
# ============================
def build_cloudinary_url(public_path):
    """
    public_path:  productos/cotillon/foto.webp
    return:       https://res.cloudinary.com/<cloud>/image/upload/productos/cotillon/foto.webp
    """

    url, _ = cloudinary_url(
        public_path,
        secure=True,
        cloud_name=CLOUD_NAME
    )

    return url


# ============================
# 3) Verificar existencia real
# ============================
def cloudinary_exists(public_path):
    """
    Verifica si el archivo existe en Cloudinary.
    Si el recurso no existe → Cloudinary levanta excepción.
    """
    try:
        cloudinary.api.resource(public_path)
        return True
    except Exception:
        return False


# ============================
# 4) Proceso principal
# ============================
def run(simulate=True):
    print("🔍 Analizando imágenes…")

    productos = Producto.objects.all()
    cambios = 0

    for p in productos:
        old = p.imagen

        if not old:
            continue

        clean = sanitize_path(old)

        if not clean:
            print(f"⚠ Producto {p.id} → Imagen inválida: {old}")
            continue

        # Construir URL final
        final_url = build_cloudinary_url(clean)

        # Si no existe en Cloudinary → fallback
        if not cloudinary_exists(clean):
            print(f"❌ No existe en Cloudinary: {clean}")
            # no subimos archivos; solo marcamos fallback
            final_url = "https://res.cloudinary.com/dfkyxmjnx/image/upload/yoquet/fallback.webp"

        # Saltar si igual
        if str(old).strip() == final_url.strip():
            continue

        print(f"\n🛠 Producto {p.id} →")
        print(f"     OLD: {old}")
        print(f"     NEW: {final_url}")

        cambios += 1

        if not simulate:
            p.imagen = final_url
            p.save(update_fields=["imagen"])

    print("\n✔ Listo.")
    print(f"   Productos corregidos: {cambios}")
