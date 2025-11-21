from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    "yoquet-disenos-backend.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://yoquet-disenos-backend.onrender.com",
    "https://yoquet-disenos-frontend.onrender.com",
]

CORS_ALLOWED_ORIGINS = [
    "https://yoquet-disenos-frontend.onrender.com",
]

# =========================================
#  SEGURIDAD HTTP
# =========================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Archivos estáticos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Forzar SSL en Render
os.environ["DJANGO_SSL_REQUIRE"] = "True"

# Cloudinary (en prod siempre activo)
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

MEDIA_URL = "/media/"

# Logging seguro
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}
