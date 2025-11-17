"""
============================================================
FIX_IMAGES FINAL 2025 — ULTRA PRO FUSION
============================================================
Reparador integral de URLs de imágenes para Yoquet Diseños.

Este script combina TODAS las funciones avanzadas:

✔ Repara rutas rotas
✔ Elimina "image/upload", "yoquet/", basura y duplicados
✔ Normaliza barras, rutas y extensiones
✔ Detecta CloudinaryResource (cuando imagen no es string)
✔ Obtiene public_id correcto de forma segura
✔ Genera URL final usando cloudinary.utils.cloudinary_url()
✔ Evita sobrescribir si la URL ya es válida
✔ Modo simulación o ejecución real
✔ Compatible con producción y desarrollo
✔ Repetible sin romper nada

Modo USO:
---------

SIMULACIÓN (NO guarda):
    python manage.py shell --command="import productos.fix_images_final as f; f.run(simulate=True)"

EJECUCIÓN REAL (GUARDA EN DB):
    python manage.py shell --command="import productos.fix_images_final as f; f.run(simulate=False)"

============================================================
Autor: conurbaDEV 
============================================================
"""

import re
from cloudinary.utils import cloudinary_url
from django.conf import settings
from productos.models import Producto


# ============================================================
# 1) Convertir cualquier input en string usable
# ============================================================
def normalize_to_string(value):
    """Convierte CloudinaryResource, None o string en string usable."""
    if value is None:
        return ""

    # CloudinaryResource → usar su URL
    if hasattr(value, "url"):
        return str(value.url)

    return str(value).strip()


# ============================================================
# 2) Detección de URL Cloudinary válida (no necesita corrección)
# ============================================================
def is_valid_cloudinary_url(url):
    if not isinstance(url, str):
        return False

    return (
        url.startswith("https://res.cloudinary.com/")
        and "/image/upload/" in url
        and "yoquet/image/upload" not in url
        and "//image/upload" not in url
    )


# ============================================================
# 3) Limpieza profunda: obtener public_id limpio
# ============================================================
def extract_public_id(raw):
    """
    Devuelve el public_id final que Cloudinary necesita:

        productos/categoria/archivo.webp

    Limpia:
        - image/upload/
        - yoquet/
        - dominios completos
        - dobles barras
        - extensiones erróneas
    """

    if not raw:
        return None

    raw = raw.lower().strip()

    # Quitar dominio completo Cloudinary si viene incluido
    raw = re.sub(
        r"https://res\.cloudinary\.com/[a-z0-9_-]+/image/upload/?",
        "",
        raw
    )

    # Eliminar basura común
    raw = raw.replace("image/upload/", "")
    raw = raw.replace("image/upload", "")
    raw = raw.replace("yoquet/", "")

    # Normalizar barras
    raw = raw.lstrip("/")
    raw = raw.replace("//", "/")

    # Normalizar extensiones
    raw = re.sub(
        r"\.(jpg|jpeg|png|gif)$",
        ".webp",
        raw,
        flags=re.IGNORECASE
    )

    return raw


# ============================================================
# 4) Generar URL final Cloudinary
# ============================================================
def generate_cloudinary_url(public_id):
    """Construye la URL oficial de Cloudinary."""
    if not public_id:
        return None

    url, _ = cloudinary_url(public_id, secure=True)
    return url


# ============================================================
# 5) Motor principal — ULTRA PRO
# ============================================================
def run(simulate=True):
    print("\n🔍 FIX_IMAGES_FINAL — Analizando imágenes…")
    print("===================================================")

    updated = 0
    skipped = 0

    for p in Producto.objects.all():

        raw = normalize_to_string(p.imagen)

        # Casos vacíos → ignorar
        if not raw:
            skipped += 1
            continue

        # Ya válida → nada que hacer
        if is_valid_cloudinary_url(raw):
            skipped += 1
            continue

        # Obtener public_id limpio
        public_id = extract_public_id(raw)
        if not public_id:
            skipped += 1
            continue

        # Construir URL final
        try:
            final_url = generate_cloudinary_url(public_id)
        except Exception as e:
            print(f"❌ Error en producto {p.id}: {e}")
            skipped += 1
            continue

        if not final_url or final_url == raw:
            skipped += 1
            continue

        # Registrar cambio
        print(f"\n🛠 Producto {p.id} → {p.nombre}")
        print(f"    OLD: {raw}")
        print(f"    NEW: {final_url}")

        # Guardar en DB si no está simulando
        if not simulate:
            p.imagen = final_url
            p.save()

        updated += 1

    print("\n===================================================")
    print("✔ PROCESO COMPLETADO")
    print(f"   Imágenes corregidas: {updated}")
    print(f"   Imágenes ignoradas:  {skipped}")
    print(f"   SIMULACIÓN: {simulate}")
    print("===================================================\n")

    return updated
