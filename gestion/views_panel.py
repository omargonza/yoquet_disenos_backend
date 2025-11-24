from django.shortcuts import render
from productos.models import Producto, Categoria

def panel_gestion(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.order_by("id")

    return render(request, "gestion/panel.html", {
        "categorias": categorias,
        "productos": productos,
    })
