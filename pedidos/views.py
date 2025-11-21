from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction

from .models import Pedido, PedidoItem
from productos.models import Producto


class CrearPedidoView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        usuario = request.user
        data = request.data

        items = data.get("items", [])
        if not items:
            return Response(
                {"error": "El carrito está vacío."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ===============================
        #  Validación de datos mínimos
        # ===============================
        campos_obligatorios = ["nombre", "email", "direccion", "metodoPago"]
        for campo in campos_obligatorios:
            if not data.get(campo):
                return Response(
                    {"error": f"El campo '{campo}' es obligatorio."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ===============================
        #  Cálculo REAL del total (anti fraude)
        # ===============================
        total_calculado = 0
        productos_validos = []

        for item in items:
            try:
                producto = Producto.objects.get(id=item["id"])
            except Producto.DoesNotExist:
                return Response(
                    {"error": f"Producto con ID {item['id']} no existe."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cantidad = max(1, int(item.get("cantidad", 1)))
            subtotal = producto.precio * cantidad

            total_calculado += subtotal
            productos_validos.append((producto, cantidad))

        # ===============================
        #  Crear pedido (transacción atómica)
        # ===============================
        pedido = Pedido.objects.create(
            usuario=usuario,
            nombre=data["nombre"],
            email=data["email"],
            direccion=data["direccion"],
            metodo_pago=data["metodoPago"],
            total=total_calculado  # total seguro desde backend
        )

        # ===============================
        #  Crear items
        # ===============================
        for producto, cantidad in productos_validos:
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            )

        return Response(
            {
                "message": "Pedido creado correctamente",
                "pedido_id": pedido.id,
                "total": total_calculado
            },
            status=status.HTTP_201_CREATED
        )
