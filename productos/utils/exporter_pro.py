import json
import os
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
from productos.models import Producto
from django.conf import settings


class ExportadorMasterPro:
    def __init__(self):
        self._configurar_logs()

    def _configurar_logs(self):
        log_dir = os.path.join(settings.BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        handler = RotatingFileHandler(
            os.path.join(log_dir, "exportador.log"),
            maxBytes=1024 * 512,
            backupCount=3,
        )

        formatter = logging.Formatter(
            "%(asctime)s — %(levelname)s — %(message)s"
        )

        handler.setFormatter(formatter)

        self.logger = logging.getLogger("exportador_master_pro")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def exportar(self, json_path="catalogo.json", excel_path="catalogo.xlsx"):
        productos = Producto.objects.all().order_by(
            "-destacado",
            "categoria__nombre",
            "nombre"
        )

        data = []

        for p in productos:
            data.append({
                "codigo": p.codigo,
                "nombre": p.nombre,
                "categoria": p.categoria.nombre,
                "precio": float(p.precio),
                "destacado": p.destacado,
                "imagen": p.imagen.url if p.imagen else None,
            })

        # JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Excel
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)

        self.logger.info(
            f"Exportación completa → JSON: {json_path} — XLSX: {excel_path}"
        )

        return {"json": json_path, "excel": excel_path}
