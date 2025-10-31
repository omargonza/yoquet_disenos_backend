from .base import *
import os

from decouple import config


DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
from decouple import config
import dj_database_url
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 🌐 Intentar usar la base de datos de Render (por DATABASE_URL)
try:
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL')
        )
    }

    # Parámetros de conexión estable
    DATABASES["default"]["CONN_MAX_AGE"] = 600
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
    DATABASES["default"]["ATOMIC_REQUESTS"] = False

    print(f"🔗 [DEV] Conectado a la base de datos de Render: {DATABASES['default']['NAME']}")

except Exception as e:
    # ⚙️ Fallback automático a SQLite si no puede conectar
    print(f"⚠️ No se pudo conectar a Render ({e}), usando SQLite local.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print(f"💾 [DEV] Usando base local: {DATABASES['default']['NAME']}")


# Desactivar SSL en entorno local
os.environ["DJANGO_SSL_REQUIRE"] = "False"


# ☁️ Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'