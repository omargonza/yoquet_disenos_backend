import os
from django.conf import settings


class ImageScanner:
    """
    Escanea media/productos/<categoria>/imagen.ext
    y devuelve diccionarios con:
    - ruta absoluta
    - archivo
    - categoría
    """

    VALID_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    def scan_media(self):
        base = os.path.join(settings.MEDIA_ROOT, "productos")

        if not os.path.exists(base):
            return []

        resultados = []

        for categoria in os.listdir(base):
            cat_path = os.path.join(base, categoria)

            if not os.path.isdir(cat_path):
                continue

            for archivo in os.listdir(cat_path):

                if not archivo.lower().endswith(self.VALID_EXT):
                    continue

                ruta = os.path.join(cat_path, archivo)

                resultados.append({
                    "ruta": ruta,
                    "archivo": archivo,
                    "categoria": categoria,
                })

        return resultados
