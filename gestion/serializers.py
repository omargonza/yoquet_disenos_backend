from rest_framework import serializers
from productos.models import Producto, Categoria

class ProductoEdicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "categoria",
            "imagen",
            "stock",
            "destacado",
        ]
