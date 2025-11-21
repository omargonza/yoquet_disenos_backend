from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# =====================================================
# 📘 Configuración Swagger / OpenAPI
# =====================================================
schema_view = get_schema_view(
    openapi.Info(
        title="Yoquet Diseños API",
        default_version="v1",
        description="API del e-commerce Yoquet Diseños",
        contact=openapi.Contact(email="aplicacionesgonza@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# =====================================================
# 🚀 Rutas principales
# =====================================================
urlpatterns = [
    # Panel Admin
    path("admin/", admin.site.urls),

    # Apps locales
    path("api/", include("productos.urls")),
    path("api/auth/", include("users.urls")),
    path("api/pedido/", include("pedidos.urls")),

    # JWT Tokens
    # 👉 Este es el login REAL
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),

    # Refresh token
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Documentación
    re_path(
        r"^api/docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api/schema/$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]

# =====================================================
# 🖼️ Archivos estáticos y media
# =====================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    print("🧩 DEBUG: Archivos media y static servidos localmente.")
