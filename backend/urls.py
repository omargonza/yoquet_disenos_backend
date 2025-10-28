from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# =====================================================
# 📘 Configuración de documentación Swagger / OpenAPI
# =====================================================
schema_view = get_schema_view(
    openapi.Info(
        title="Yoquet Diseños API",
        default_version="v1",
        description="API de e-commerce (Django REST Framework + JWT + Cloudinary)",
        contact=openapi.Contact(email="yoquet@disenos.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# =====================================================
# 🚀 Rutas principales
# =====================================================
urlpatterns = [
    # 🧩 Administración Django
    path("admin/", admin.site.urls),

    # 🛍️ Apps del proyecto
    path("api/", include("productos.urls")),
    path("api/auth/", include("users.urls")),

    # 🔐 Endpoints JWT (SimpleJWT)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 📄 Documentación Swagger / JSON Schema
    re_path(r"^api/docs/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path(r"^api/schema/$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]

# =====================================================
# 🖼️ Archivos estáticos y media
# =====================================================
# En local (DEBUG=True): servir archivos desde /media/
# En producción (Render / Cloudinary): los media se cargan desde Cloudinary automáticamente.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    print("🧩 DEBUG mode: sirviendo archivos estáticos y media desde local.")
else:
    print("☁️ Producción: Cloudinary maneja los archivos media.")
