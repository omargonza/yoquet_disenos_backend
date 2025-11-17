from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 🔐 Seguridad
SECRET_KEY = config('DJANGO_SECRET_KEY', default='change-me')
DEBUG = config('DJANGO_DEBUG', cast=bool, default=True)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='*')
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(',')] if isinstance(ALLOWED_HOSTS, str) else ['*']

# 🧩 Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    # externas
    'rest_framework', 'corsheaders', 'django_filters', 'drf_yasg',
    # locales
    'productos', 'users',
    'cloudinary_storage',
    'cloudinary',
]


# ⚙️ Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'backend.wsgi.application'
# 🧱 Configuración de base de datos (automática: local o Render)


# 🧱 Configuración de base de datos (automática: local o Render)
from decouple import config
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# Opciones opcionales (mantienen estabilidad)
DATABASES["default"]["CONN_MAX_AGE"] = 600
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DATABASES["default"]["ATOMIC_REQUESTS"] = False

print(f"🔗 Conectado a la base de datos: {DATABASES['default']['NAME']}")


# 🔒 Validadores
AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌎 Internacionalización
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# 🧾 Archivos estáticos y media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# 🌐 CORS y CSRF (se heredan)
CORS_ALLOWED_ORIGINS = [o.strip() for o in config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173').split(',')]
csrf = config('CSRF_TRUSTED_ORIGINS', default='')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf.split(',')] if csrf else []

# ⚙️ DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 16,
}

# ☁️ Cloudinary configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}
print("🔥 CLOUDINARY DEBUG >>>")
print("CLOUD_NAME:", config('CLOUDINARY_CLOUD_NAME'))
print("API_KEY:", config('CLOUDINARY_API_KEY'))
print("API_SECRET:", config('CLOUDINARY_API_SECRET'))

# === MEDIA (se usa en DEV y PRD) ===
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
