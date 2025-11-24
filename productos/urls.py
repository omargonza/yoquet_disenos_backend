from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaViewSet,
    ProductoViewSet,
    ProductosDestacadosView,
    ProductosPorCategoriaView,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')

urlpatterns = [
    # Rutas personalizadas primero
    path('productos/destacados/', ProductosDestacadosView.as_view(),
         name='productos_destacados'),

    path('productos/por-categoria/<int:categoria_id>/',
         ProductosPorCategoriaView.as_view(),
         name='productos_por_categoria'),

    # ViewSets
    path('', include(router.urls)),
]
