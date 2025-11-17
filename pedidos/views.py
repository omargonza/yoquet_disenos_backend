from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Pedido, PedidoItem
from productos.models import Producto

class CrearPedidoView(APIView):
    authentication_classes = [JWTAuthentication]

    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(">>> TOKEN RECIBIDO:", request.META.get("HTTP_AUTHORIZATION"))
        print(">>> USUARIO:", request.user)
        print(">>> AUTENTICADO:", request.user.is_authenticated)

        usuario = request.user
        data = request.data

        items = data.get("items", [])
        if not items:
            return Response({"error": "El carrito está vacío."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            nombre=data.get("nombre"),
            email=data.get("email"),
            direccion=data.get("direccion"),
            metodo_pago=data.get("metodoPago"),
            total=data.get("total"),
        )

        # Crear items
        for item in items:
            producto = Producto.objects.get(id=item["id"])
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item["cantidad"],
                precio_unitario=producto.precio,
            )

        return Response({"message": "Pedido creado correctamente", "pedido_id": pedido.id},
                        status=status.HTTP_201_CREATED)
