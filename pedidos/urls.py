from django.urls import path
from .views import CrearPedidoView

urlpatterns = [
    path("crear/", CrearPedidoView.as_view(), name="crear_pedido"),
]
