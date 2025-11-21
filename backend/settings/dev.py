# ================================
#  DEV SETTINGS (entorno local)
# ================================
from .base import *
import os
from decouple import config
import dj_database_url
from pathlib import Path

DEBUG = True

# Permitir solo local
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# CORS para Vite
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# ================================
# 🗄 Base de datos (Render → local)
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    DATABASES = {
        "default": dj_database_url.parse(
            config("DATABASE_URL")
        )
    }

    DATABASES["default"]["CONN_MAX_AGE"] = 600
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
    DATABASES["default"]["ATOMIC_REQUESTS"] = False

    print(f"🔗 [DEV] Conectado a Render DB: {DATABASES['default']['NAME']}")

except Exception as e:
    print(f"⚠️ Render no disponible ({e}), usando SQLite local.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    print(f"💾 [DEV] Usando SQLite: {DATABASES['default']['NAME']}")

# Desactivar SSL en local
os.environ["DJANGO_SSL_REQUIRE"] = "False"


# ================================
# ☁️ Cloudinary (solo si hay claves)
# ================================
cloud_name = config("CLOUDINARY_CLOUD_NAME", default="")
api_key = config("CLOUDINARY_API_KEY", default="")
api_secret = config("CLOUDINARY_API_SECRET", default="")

if cloud_name and api_key and api_secret:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": cloud_name,
        "API_KEY": api_key,
        "API_SECRET": api_secret,
    }
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    print("⚠️ Cloudinary no configurado en dev.")
