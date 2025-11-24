from django.urls import path
from .views_panel import panel_gestion

urlpatterns = [
    path("panel/", panel_gestion),
]
