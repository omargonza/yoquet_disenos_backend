import os
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings
from django.db import transaction
from productos.models import Producto


class SyncerMasterPro:
    """
    Sincronizador empresarial:
    - Compatible Cloudinary (no sobrescribe URLs)
    - Logs rotativos
    - Rollback ante error
    - Asignación por coincidencia de código
    """

    def __init__(self):
        self._configurar_logs()

    def _configurar_logs(self):
        log_dir = os.path.join(settings.BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, "syncer.log")

        self.logger = logging.getLogger("syncer_master_pro")
        self.logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(
            log_path,
            maxBytes=1024 * 512,
            backupCount=5
        )
        formatter = logging.Formatter(
            "%(asctime)s — %(levelname)s — %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def sync(self):
        media_path = settings.MEDIA_ROOT
        files = os.listdir(media_path)
        productos = Producto.objects.all()

        resultados = {
            "asignadas": 0,
            "omitidas": 0,
            "errores": 0
        }

        try:
            with transaction.atomic():
                for f in files:
                    nombre = f.lower()

                    # productos cuyo código coincide con el nombre de archivo
                    candidatos = productos.filter(codigo__icontains=nombre)

                    if not candidatos:
                        resultados["omitidas"] += 1
                        self.logger.warning(f"No hay producto para imagen: {f}")
                        continue

                    for p in candidatos:
                        # si ya tiene URL Cloudinary, NO tocar
                        if p.imagen and str(p.imagen).startswith("http"):
                            self.logger.info(
                                f"Omitiendo {p.codigo} — tiene URL Cloudinary"
                            )
                            continue

                        try:
                            p.imagen.name = f
                            p.save()
                            resultados["asignadas"] += 1
                            self.logger.info(f"Imagen asignada: {f} → {p.codigo}")
                        except Exception as e:
                            resultados["errores"] += 1
                            self.logger.error(
                                f"ERROR asignando imagen {f} a {p.codigo} — {e}"
                            )
                            raise e  # rollback
        except Exception:
            self.logger.error("ROLLBACK GENERAL — sincronización abortada.")
            return resultados

        self.logger.info(f"SINCRONIZACIÓN COMPLETA — {resultados}")
        return resultados
