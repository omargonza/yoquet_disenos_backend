from .base import *
import os
import sys

DEBUG = False

ALLOWED_HOSTS = [
    'yoquet-disenos-backend.onrender.com',
    'localhost',
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = [
    'https://yoquet-disenos-backend.onrender.com',
    'https://yoquet-disenos-frontend.onrender.com',
]

CORS_ALLOWED_ORIGINS = [
    "https://yoquet-disenos-frontend.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Forzamos SSL en Render
os.environ["DJANGO_SSL_REQUIRE"] = "True"

# ⚠️ IMPORTANTE: ya no agregamos cloudinary_storage aquí,
# porque ya está en base.py
# INSTALLED_APPS += ['cloudinary_storage']  ❌ eliminado

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

MEDIA_URL = '/media/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
