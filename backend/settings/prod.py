from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    'yoquet-disenos-backend.onrender.com',
    'localhost',
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = [
    'https://yoquet-disenos-backend.onrender.com',
    'https://omargonza.github.io',
]

CORS_ALLOWED_ORIGINS = [
    'https://omargonza.github.io',
    'https://omargonza.github.io/yoquet_disenos_frontend',
]

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
