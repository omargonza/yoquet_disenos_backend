from django.core.management.base import BaseCommand
from gestion.utils.scanner import ImageScanner
from gestion.utils.generator import ProductGenerator


class Command(BaseCommand):
    help = "Genera productos automáticos desde imágenes en media/"

    def handle(self, *args, **opts):
        scanner = ImageScanner()
        archivos = scanner.scan_media()

        generator = ProductGenerator()
        creados = generator.generar_desde_media(archivos)

        self.stdout.write(self.style.SUCCESS(f"Productos creados: {len(creados)}"))
