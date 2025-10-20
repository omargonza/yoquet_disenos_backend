import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
import django

# === 📁 CONFIGURACIÓN BASE ===
# Este script se ejecuta desde: yoquet_disenos_full/backend

BASE_DIR = Path(__file__).resolve().parent.parent  # donde está manage.py
PROJECT_DIR = BASE_DIR / "backend"  # donde está settings.py

# Permitir que Django encuentre el proyecto
sys.path.append(str(BASE_DIR))
sys.path.append(str(PROJECT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.dev")

# Importante: movernos al directorio base antes de inicializar Django
os.chdir(BASE_DIR)
django.setup()

# === 📦 IMPORTAR MODELOS ===
from productos.models import Producto, Categoria

MEDIA_DIR = BASE_DIR / "media" / "productos"
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

print("⚠️  Este script permite limpiar el catálogo de productos.")
print("Opciones disponibles:")
print("  1️⃣  Borrar solo productos (mantener categorías e imágenes)")
print("  2️⃣  Borrar productos + imágenes (mantener categorías)")
print("  3️⃣  Borrar TODO (productos, categorías e imágenes)")
opcion = input("\nSelecciona una opción (1 / 2 / 3): ").strip()

if opcion not in ("1", "2", "3"):
    print("❎ Opción inválida. Cancelado.")
    sys.exit()

confirm = input("¿Seguro que deseas continuar con la limpieza? (s/n): ").strip().lower()
if confirm != "s":
    print("❎ Operación cancelada.")
    sys.exit()

# === 💾 GENERAR RESPALDO ===
fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = BACKUP_DIR / f"respaldo_catalogo_{fecha}.json"

productos_data = list(Producto.objects.all().values())
categorias_data = list(Categoria.objects.all().values())

backup_data = {"categorias": categorias_data, "productos": productos_data}

with open(backup_path, "w", encoding="utf-8") as f:
    json.dump(backup_data, f, indent=2, ensure_ascii=False)

print(f"💾 Respaldo guardado en: {backup_path}")
print(f"   ({len(categorias_data)} categorías, {len(productos_data)} productos)")

# === 🧹 LIMPIEZA ===
if opcion == "1":
    print("\n🗑️  Borrando solo productos (categorías e imágenes se conservan)...")
    Producto.objects.all().delete()

elif opcion == "2":
    print("\n🗑️  Borrando productos e imágenes (categorías se conservan)...")
    Producto.objects.all().delete()
    if MEDIA_DIR.exists():
        shutil.rmtree(MEDIA_DIR)
        print("🧹 Carpeta media/productos eliminada.")

elif opcion == "3":
    print("\n🔥 Borrando productos, categorías e imágenes...")
    Producto.objects.all().delete()
    Categoria.objects.all().delete()
    if MEDIA_DIR.exists():
        shutil.rmtree(MEDIA_DIR)
        print("🧹 Carpeta media/productos eliminada.")

print("\n✅ Limpieza completada correctamente.")
print("\n👉 Próximos pasos sugeridos:")
print("   python procesar_catalogos.py")
print("   python manage.py loaddata productos_iniciales.json")
print(f"\n📂 Si necesitás restaurar, usá el respaldo ubicado en:\n   {backup_path}")
