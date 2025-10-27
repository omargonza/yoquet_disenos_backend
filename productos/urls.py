from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, ProductosDestacadosView

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categorias")
router.register("productos", ProductoViewSet, basename="productos")

urlpatterns = [
    path("productos/destacados/", ProductosDestacadosView.as_view(), name="productos-destacados"),
]

urlpatterns += router.urls
