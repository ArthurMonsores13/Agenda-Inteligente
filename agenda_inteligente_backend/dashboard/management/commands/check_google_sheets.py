from django.core.management.base import BaseCommand

from agenda_inteligente_backend.dashboard.services import DashboardService


class Command(BaseCommand):
    help = "Testa a conexao com Google Sheets e mostra um resumo das linhas encontradas."

    def handle(self, *args, **options):
        service = DashboardService()
        rows = service._load_rows()

        self.stdout.write(self.style.SUCCESS(f"Fonte: {service.data_source}"))
        self.stdout.write(self.style.SUCCESS(f"Linhas encontradas: {len(rows)}"))

        if rows:
            columns = ", ".join(rows[0].keys())
            self.stdout.write(f"Colunas: {columns}")
