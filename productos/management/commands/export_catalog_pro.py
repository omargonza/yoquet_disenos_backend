from django.core.management.base import BaseCommand
from productos.utils.exporter_pro import ExportadorMasterPro


class Command(BaseCommand):
    help = "Exportador MASTER PRO — JSON + XLSX"

    def add_arguments(self, parser):
        parser.add_argument(
            "--json", default="catalogo.json", type=str
        )
        parser.add_argument(
            "--excel", default="catalogo.xlsx", type=str
        )

    def handle(self, *args, **opts):
        exp = ExportadorMasterPro()
        res = exp.exportar(json_path=opts["json"], excel_path=opts["excel"])
        self.stdout.write(self.style.SUCCESS("Exportación completada"))
        self.stdout.write(str(res))
