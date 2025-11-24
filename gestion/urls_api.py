from django.urls import path
from .views import (
    EscanearImagenes,
    ProductosPendientes,
    UpdateLote,
)

urlpatterns = [
    path("escanear/", EscanearImagenes.as_view()),
    path("pendientes/", ProductosPendientes.as_view()),
    path("update/", UpdateLote.as_view()),
]
