# productos/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Lectura para todos, escritura solo admin/staff."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'orden']


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related('categoria').all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion', 'categoria__nombre']
    ordering_fields = ['precio', 'nombre', 'creado', 'actualizado', 'orden']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ProductosDestacadosView(ListAPIView):
    """ /api/productos/destacados/ """
    serializer_class = ProductoSerializer

    def get_queryset(self):
        qs = Producto.objects.filter(destacado=True).order_by("-actualizado")
        return qs[:12]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ProductosPorCategoriaView(ListAPIView):
    """ /api/productos/por-categoria/<categoria_id>/ """
    serializer_class = ProductoSerializer

    def get_queryset(self):
        categoria_id = self.kwargs['categoria_id']
        return (
            Producto.objects
            .filter(categoria_id=categoria_id)
            .select_related('categoria')
            .order_by('orden', '-destacado', 'nombre')
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class CrearPedidoView(APIView):
    """
    Vista de Checkout — requiere autenticación.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        usuario = request.user
        data = request.data

        items = data.get("items", [])
        if not items:
            return Response({"error": "El carrito está vacío."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Pedido creado correctamente", "usuario": usuario.username},
            status=status.HTTP_201_CREATED
        )
