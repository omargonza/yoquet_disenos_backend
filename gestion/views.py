from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from productos.models import Producto
from .serializers import ProductoEdicionSerializer
from .utils.scanner import ImageScanner
from .utils.generator import ProductGenerator

class EscanearImagenes(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        scanner = ImageScanner()
        items = scanner.scan_media()

        generator = ProductGenerator()
        creados = generator.generar_desde_media(items)

        s = ProductoEdicionSerializer(creados, many=True)
        return Response(s.data, status=status.HTTP_201_CREATED)



class ProductosPendientes(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Producto.objects.filter(precio=0)
        s = ProductoEdicionSerializer(qs, many=True)
        return Response(s.data)


class UpdateLote(APIView):
    permission_classes = [AllowAny]

    def put(self, request):
        for item in request.data:
            p = Producto.objects.get(id=item["id"])
            s = ProductoEdicionSerializer(p, data=item, partial=True)
            s.is_valid(raise_exception=True)
            s.save()
        return Response({"status": "ok"})
