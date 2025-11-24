import os
import pandas as pd
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings
from django.db import transaction
from productos.models import Categoria, Producto


class ImportadorMasterPro:
    """
    Importador empresarial con:
    - Validaciones duras
    - Rollback automático
    - Logs rotativos
    - Soporte para Cloudinary (URL)
    - Soporte para media local
    - Control de duplicados
    """

    def __init__(self, archivo):
        self.archivo = archivo
        self._configurar_logs()

    def _configurar_logs(self):
        log_dir = os.path.join(settings.BASE_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, "importador.log")

        self.logger = logging.getLogger("importador_master_pro")
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

    def cargar(self):
        df = self._leer_archivo()
        self._validar_columnas(df)

        resultados = {
            "creados": 0,
            "actualizados": 0,
            "errores": 0
        }

        try:
            with transaction.atomic():
                for _, row in df.iterrows():
                    try:
                        self._procesar_fila(row, resultados)
                    except Exception as e:
                        resultados["errores"] += 1
                        self.logger.error(f"Error procesando fila: {row} — {e}")
                        raise e  # fuerza rollback general
        except Exception:
            self.logger.error("ROLLBACK GENERAL — importación abortada.")
            return resultados

        self.logger.info(f"IMPORTACIÓN FINALIZADA — {resultados}")
        return resultados

    def _leer_archivo(self):
        ext = self.archivo.lower()

        if ext.endswith(".csv"):
            df = pd.read_csv(self.archivo)
        elif ext.endswith(".xlsx"):
            df = pd.read_excel(self.archivo)
        else:
            raise ValueError("Formato no soportado. Use CSV o XLSX.")

        self.logger.info(f"Archivo cargado correctamente: {self.archivo}")
        return df

    def _validar_columnas(self, df):
        columnas_obligatorias = {"codigo", "nombre", "precio", "categoria"}

        faltantes = columnas_obligatorias - set(df.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas obligatorias: {faltantes}")

    def _procesar_fila(self, row, resultados):
        categoria, _ = Categoria.objects.get_or_create(
            nombre=str(row["categoria"]).strip()
        )

        prod, created = Producto.objects.update_or_create(
            codigo=str(row["codigo"]).strip(),
            defaults={
                "nombre": str(row["nombre"]).strip(),
                "precio": float(row["precio"]),
                "descripcion": row.get("descripcion", ""),
                "categoria": categoria,
                "destacado": bool(row.get("destacado", False)),
            },
        )

        if created:
            resultados["creados"] += 1
            self.logger.info(f"Producto creado: {prod.codigo}")
        else:
            resultados["actualizados"] += 1
            self.logger.info(f"Producto actualizado: {prod.codigo}")

        # imagen automática (Cloudinary + local)
        self._asignar_imagen(prod, row)

    def _asignar_imagen(self, prod, row):
        if "imagen" not in row or pd.isna(row["imagen"]):
            return

        filename = str(row["imagen"]).strip()

        # 1) Si es URL (Cloudinary)
        if filename.startswith("http://") or filename.startswith("https://"):
            prod.imagen = filename
            prod.save()
            self.logger.info(f"URL Cloudinary asignada: {filename} → {prod.codigo}")
            return

        # 2) Imagen local (desarrollo)
        path = os.path.join(settings.MEDIA_ROOT, filename)

        if os.path.exists(path):
            prod.imagen.name = filename
            prod.save()
            self.logger.info(f"Imagen local asignada: {filename} → {prod.codigo}")
        else:
            self.logger.warning(
                f"Imagen no encontrada en media/ ni es URL válida: {filename}"
            )
