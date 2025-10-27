import os
import sys
import json
from io import BytesIO
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from PIL import Image
import fitz  # PyMuPDF
from tqdm import tqdm

# === Inicializar Django ===
import django
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "backend"
sys.path.extend([str(BASE_DIR), str(PROJECT_DIR)])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.dev")
django.setup()

from productos.models import Producto, Categoria

# === Configuración ===
CATALOGOS_DIR = BASE_DIR / "catalogos"
MEDIA_DIR = BASE_DIR / "media" / "productos"
FIXTURES_DIR = BASE_DIR / "productos" / "fixtures"
FIXTURE_PATH = FIXTURES_DIR / "productos_iniciales.json"

CATEGORIAS_BASE = ["Cotillón", "Navidad", "Fibrofacil", "Decoración", "Souvenir"]

IMG_DIM = 800
IMG_QUALITY = 80
MIN_IMG_W = 80
MIN_IMG_H = 80


# === Utilidades base ===
def slugify(text: str) -> str:
    t = (text or "").strip().lower()
    reemplazos = {
        "á":"a","é":"e","í":"i","ó":"o","ú":"u","ñ":"n",
        "ä":"a","ë":"e","ï":"i","ö":"o","ü":"u",
        "/":"-","\\":"-"," ":"-","--":"-",
    }
    for k,v in reemplazos.items():
        t = t.replace(k,v)
    while "--" in t:
        t = t.replace("--","-")
    return "".join(c for c in t if c.isalnum() or c in "-_").strip("-_") or "item"


def optimizar_imagen(img_bytes: bytes, salida_path: Path) -> str:
    salida_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    img.thumbnail((IMG_DIM, IMG_DIM))

    fondo = Image.new("RGB", (IMG_DIM, IMG_DIM), (248, 244, 235))  # fondo beige
    x = (IMG_DIM - img.width) // 2
    y = (IMG_DIM - img.height) // 2
    fondo.paste(img, (x, y))

    salida_path = salida_path.with_suffix(".webp")
    fondo.save(salida_path, "webp", quality=IMG_QUALITY)
    return str(salida_path.relative_to(BASE_DIR / "media")).replace("\\", "/")


def detectar_categoria(texto: str) -> str:
    t = (texto or "").lower()
    if any(x in t for x in ["vela","bengala","topper","cotillon","cotillón","cumple","globos"]):
        return "Cotillón"
    if any(x in t for x in ["navidad","arbol","árbol","papa noel","papá noel","reno","guirnalda"]):
        return "Navidad"
    if any(x in t for x in ["fibrofacil","fibrofácil","mdf","bandeja","portavino","cajon","organizador"]):
        return "Fibrofacil"
    if any(x in t for x in ["adorno","decoracion","decoración","cuadro","centro de mesa","marco"]):
        return "Decoración"
    return "Souvenir"


def get_or_create_categorias_base():
    existentes = {c.nombre for c in Categoria.objects.all()}
    for nombre in CATEGORIAS_BASE:
        if nombre not in existentes:
            Categoria.objects.create(nombre=nombre, descripcion=f"Productos de {nombre.lower()}.")
def obtener_categoria(nombre: str) -> Categoria:
    # Convertir a minúsculas para normalizar
    nombre = nombre.strip().lower()

    # Normalización definitiva (sin excepción)
    replacements = {
        "cotillon": "Cotillón",
        "cotillón": "Cotillón",
        "decoracion": "Decoración",
        "decoración": "Decoración",
        "fibrofacil": "Fibrofacil",
        "fibrofácil": "Fibrofacil",
        "souvenir": "Souvenir",
        "navidad": "Navidad",
    }

    nombre_normalizado = replacements.get(nombre, nombre.title())

    obj, _ = Categoria.objects.get_or_create(
        nombre=nombre_normalizado,
        defaults={"descripcion": f"Productos de {nombre_normalizado.lower()}."}
    )
    return obj


def producto_ya_existe(nombre: str, categoria: Categoria) -> bool:
    return Producto.objects.filter(nombre__iexact=nombre.strip(), categoria=categoria).exists()


def crear_o_actualizar_producto(nombre: str, categoria: Categoria, descripcion: str, ruta_media_rel: str):
    if producto_ya_existe(nombre, categoria):
        prod = Producto.objects.get(nombre__iexact=nombre.strip(), categoria=categoria)
        if descripcion and not prod.descripcion:
            prod.descripcion = descripcion
        if ruta_media_rel and (not prod.imagen or str(prod.imagen) != ruta_media_rel):
            prod.imagen = ruta_media_rel
        prod.save()
        return False
    else:
        Producto.objects.create(
            categoria=categoria,
            nombre=nombre.strip(),
            descripcion=descripcion or "",
            precio=Decimal("0.00"),
            stock=0,
            destacado=False,
            imagen=ruta_media_rel or "",
        )
        return True


# === NUEVO — reconstrucción desde media/productos/ ===
def nombre_pretty(nombre_archivo: str) -> str:
    palabras = nombre_archivo.replace("-", " ").replace("_", " ").split()
    return " ".join(p.capitalize() for p in palabras)


def procesar_media_productos():
    print("🖼 Procesando imágenes desde media/productos/ ...")
    get_or_create_categorias_base()

    for carpeta in MEDIA_DIR.iterdir():
        if carpeta.is_dir():
            categoria = obtener_categoria(carpeta.name)
            print(f"\n📂 Categoría: {categoria.nombre}")
            for img_path in carpeta.glob("*.webp"):
                nombre_producto = nombre_pretty(img_path.stem)
                ruta_rel = str(img_path.relative_to(BASE_DIR / "media")).replace("\\", "/")
                creado = crear_o_actualizar_producto(nombre_producto, categoria, "", ruta_rel)

                msg = "➕ Creado" if creado else "🔁 Actualizado"
                print(f"   {msg}: {nombre_producto} ({categoria.nombre})")

    print("✅ Finalizado procesamiento desde media/productos/")


# === Flujo principal ===
def procesar_catalogos():
    print("🚀 Iniciando procesamiento de catálogos…")

    # Si NO hay PDFs → reconstruimos desde media/
    if not CATALOGOS_DIR.exists() or not any(CATALOGOS_DIR.glob("*.pdf")):
        print("🟨 No hay PDFs. Usando media/productos/ como fuente.")
        procesar_media_productos()
        return

    # === Procesamiento de PDFs ===
    pdfs = sorted([p for p in CATALOGOS_DIR.glob("*.pdf") if p.is_file()])
    if not pdfs:
        print("🟨 No se encontraron PDFs en catalogos/.")
        return

    get_or_create_categorias_base()

    total_paginas = 0
    creados = actualizados = saltadas = guardadas_img = 0

    for pdf_path in pdfs:
        print(f"\n📘 Procesando: {pdf_path.name}")
        with fitz.open(pdf_path) as doc:
            for page in tqdm(doc, desc=f"Páginas de {pdf_path.stem}", unit="pág"):
                total_paginas += 1
                texto = (page.get_text("text") or "").strip()
                categoria_nombre = detectar_categoria(texto)
                categoria = obtener_categoria(categoria_nombre)
                imagenes = page.get_images(full=True)

                if not imagenes:
                    saltadas += 1
                    continue

                for i, img in enumerate(imagenes, start=1):
                    try:
                        xref = img[0]
                        base_img = doc.extract_image(xref)
                        image_bytes = base_img["image"]
                        tmp = Image.open(BytesIO(image_bytes))
                        w, h = tmp.size
                        if w < MIN_IMG_W or h < MIN_IMG_H:
                            continue

                        base_name = base_img.get("name") or f"{pdf_path.stem}-{page.number+1}-{i}"
                        nombre_img = slugify(base_name)
                        carpeta = slugify(categoria_nombre)
                        salida = MEDIA_DIR / carpeta / f"{nombre_img}.webp"
                        ruta_rel = optimizar_imagen(image_bytes, salida)
                        guardadas_img += 1

                        nombre_producto = f"{pdf_path.stem} {page.number+1}-{i}"
                        descripcion = " ".join(texto.split())[:160]
                        creado = crear_o_actualizar_producto(nombre_producto, categoria, descripcion, ruta_rel)
                        if creado: creados += 1
                        else: actualizados += 1

                    except Exception as e:
                        print(f"⚠️ Error: imagen {i}, pág {page.number+1}: {e}")
                        continue

    # === Exportar fixture ===
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    data = []

    for obj in Categoria.objects.order_by("nombre"):
        data.append({
            "model": "productos.categoria",
            "pk": obj.pk,
            "fields": {
                "nombre": obj.nombre,
                "descripcion": obj.descripcion or "",
                "creado": datetime.now().isoformat(),
            }
        })

    for prod in Producto.objects.select_related("categoria").all():
        data.append({
            "model": "productos.producto",
            "pk": prod.pk,
            "fields": {
                "categoria": prod.categoria.pk if prod.categoria else None,
                "nombre": prod.nombre,
                "descripcion": prod.descripcion or "",
                "precio": float(prod.precio or 0),
                "stock": prod.stock,
                "destacado": prod.destacado,
                "imagen": str(prod.imagen) if prod.imagen else "",
                "creado": datetime.now().isoformat(),
                "actualizado": datetime.now().isoformat(),
            }
        })

    with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    asignar_destacados_balanceado()

    print("\n✅ Procesamiento finalizado")
    print(f"📄 PDFs: {len(pdfs)}")
    print(f"🗂 Páginas: {total_paginas}")
    print(f"🖼 Imágenes nuevas: {guardadas_img}")
    print(f"🆕 Productos creados: {creados}")
    print(f"🔁 Productos actualizados: {actualizados}")
    print(f"🧾 Fixture guardado en: {FIXTURE_PATH}")
    
def asignar_destacados_balanceado():
    print("✨ Asignando productos destacados de forma balanceada...")

    # Limpiamos destacados existentes
    Producto.objects.update(destacado=False)

    categorias = Categoria.objects.all().order_by("orden", "nombre")

    for categoria in categorias:
        productos = Producto.objects.filter(categoria=categoria).order_by("-actualizado")[:3]
        for p in productos:
            p.destacado = True
            p.save(update_fields=["destacado"])
            print(f"   ⭐ {p.nombre}  ({categoria.nombre})")

    print("✅ Destacados asignados automáticamente")


if __name__ == "__main__":
    procesar_catalogos()
    asignar_destacados_balanceado()
