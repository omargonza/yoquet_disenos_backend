from django.core.management.base import BaseCommand
from productos.utils.syncer_pro import SyncerMasterPro


class Command(BaseCommand):
    help = "Sincronizador MASTER PRO — imágenes ↔ productos"

    def handle(self, *args, **opts):
        resultados = SyncerMasterPro().sync()
        self.stdout.write(self.style.SUCCESS("Sincronización finalizada"))
        self.stdout.write(str(resultados))
