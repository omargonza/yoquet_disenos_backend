from rest_framework import serializers
from .models import Pedido, PedidoItem

class PedidoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoItem
        fields = ["producto", "cantidad", "precio_unitario"]

class PedidoSerializer(serializers.ModelSerializer):
    items = PedidoItemSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ["id", "usuario", "nombre", "email", "direccion", "metodo_pago", "total", "items"]
