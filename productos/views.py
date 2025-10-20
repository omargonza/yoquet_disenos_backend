from rest_framework import viewsets, permissions, filters
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset=Categoria.objects.all()
    serializer_class=CategoriaSerializer
    permission_classes=[IsAdminOrReadOnly]
    filter_backends=[filters.SearchFilter, filters.OrderingFilter]
    search_fields=['nombre','descripcion']
    ordering_fields=['nombre']

class ProductoViewSet(viewsets.ModelViewSet):
    queryset=Producto.objects.select_related('categoria').all()
    serializer_class=ProductoSerializer
    permission_classes=[IsAdminOrReadOnly]
    filter_backends=[filters.SearchFilter, filters.OrderingFilter]
    search_fields=['nombre','descripcion','categoria__nombre']
    ordering_fields=['precio','nombre','creado']
