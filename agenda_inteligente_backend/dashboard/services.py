from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError
import csv
import io
import os

import gspread

from agenda_inteligente_backend.appointments.models import Appointment
from sheet_dashboard_analyzer import build_dashboard_from_sheet_rows


@dataclass
class DashboardFilters:
    start_date: date | None = None
    end_date: date | None = None
    statuses: list[str] | None = None


class DashboardService:
    """
    Busca registros no Google Sheets, aplica filtros e gera a resposta
    estruturada para o dashboard do Next.js.
    """

    def __init__(
        self,
        spreadsheet_id: str | None = None,
        worksheet_name: str | None = None,
        credentials_path: str | None = None,
    ) -> None:
        self.spreadsheet_id = spreadsheet_id or os.environ.get("GSHEETS_SPREADSHEET_ID", "")
        self.worksheet_name = worksheet_name or os.environ.get("GSHEETS_WORKSHEET_NAME", "Agendamentos")
        self.credentials_path = credentials_path or os.environ.get("GSHEETS_CREDENTIALS_PATH", "")
        self.public_csv_url = os.environ.get("GSHEETS_PUBLIC_CSV_URL", "")
        self.data_source = "database"

    def get_dashboard(self, filters: DashboardFilters | None = None) -> dict[str, Any]:
        filters = filters or DashboardFilters()
        rows = self._load_rows()
        filtered_rows = self._apply_filters(rows, filters)
        dashboard = build_dashboard_from_sheet_rows(filtered_rows)

        dashboard["filters"] = {
            "start_date": filters.start_date.isoformat() if filters.start_date else None,
            "end_date": filters.end_date.isoformat() if filters.end_date else None,
            "statuses": filters.statuses or [],
        }
        dashboard["metadata"] = {
            "spreadsheet_id": self.spreadsheet_id,
            "worksheet_name": self.worksheet_name,
            "data_source": self.data_source,
            "total_rows_before_filters": len(rows),
            "total_rows_after_filters": len(filtered_rows),
        }
        return dashboard

    def _load_rows(self) -> list[dict[str, Any]]:
        if self.public_csv_url:
            return self._load_rows_from_public_csv(self.public_csv_url)

        if not self.spreadsheet_id:
            return self._load_rows_from_database()

        if not self.credentials_path:
            raise ValueError("GSHEETS_CREDENTIALS_PATH nao configurado.")
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credencial do Google Sheets nao encontrada: {self.credentials_path}")

        client = gspread.service_account(filename=self.credentials_path)
        worksheet = client.open_by_key(self.spreadsheet_id).worksheet(self.worksheet_name)
        self.data_source = "google_sheets"
        return worksheet.get_all_records()

    def _load_rows_from_public_csv(self, csv_url: str) -> list[dict[str, Any]]:
        url = csv_url
        if csv_url == "auto":
            if not self.spreadsheet_id:
                return self._load_rows_from_database()
            sheet_name = quote(self.worksheet_name)
            url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

        try:
            with urlopen(url, timeout=20) as response:
                csv_text = response.read().decode("utf-8-sig")
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise PermissionError(
                    "Google Sheets retornou acesso negado. Compartilhe a planilha como "
                    "'Qualquer pessoa com o link' ou use Arquivo > Compartilhar > "
                    "Publicar na web e informe o link CSV em GSHEETS_PUBLIC_CSV_URL."
                ) from exc
            raise

        self.data_source = "google_sheets_public_csv"
        return list(csv.DictReader(io.StringIO(csv_text)))

    def _load_rows_from_database(self) -> list[dict[str, Any]]:
        self.data_source = "database"
        return [
            {
                "Nome": appointment.patient_name,
                "Telefone": appointment.phone,
                "Data": appointment.appointment_date.isoformat(),
                "Horario": appointment.appointment_time.strftime("%H:%M"),
                "Servico": appointment.service,
                "Status": appointment.status,
                "Motivo Cancelamento": appointment.cancellation_reason,
                "Observacoes": appointment.notes,
            }
            for appointment in Appointment.objects.all()
        ]

    def _apply_filters(
        self,
        rows: list[dict[str, Any]],
        filters: DashboardFilters,
    ) -> list[dict[str, Any]]:
        filtered = rows
        if filters.statuses:
            allowed = {status.casefold() for status in filters.statuses}
            status_filtered: list[dict[str, Any]] = []
            for row in filtered:
                row_status = self._extract_status(row)
                if row_status and row_status.casefold() in allowed:
                    status_filtered.append(row)
            filtered = status_filtered

        if filters.start_date or filters.end_date:
            filtered = [row for row in filtered if self._date_matches(row, filters.start_date, filters.end_date)]

        return filtered

    def _extract_status(self, row: dict[str, Any]) -> str | None:
        for key in row.keys():
            slug = self._slug(key)
            if slug in {"status", "situacao", "estado"}:
                value = row.get(key)
                return str(value).strip() if value not in (None, "") else None
        return None

    def _extract_date(self, row: dict[str, Any]) -> date | None:
        for key, value in row.items():
            if self._slug(key) not in {"data", "date", "agendamento_data", "appointment_date"}:
                continue
            parsed = self._try_parse_date(value)
            if parsed:
                return parsed
        return None

    def _date_matches(self, row: dict[str, Any], start_date: date | None, end_date: date | None) -> bool:
        row_date = self._extract_date(row)
        if row_date is None:
            return False
        if start_date and row_date < start_date:
            return False
        if end_date and row_date > end_date:
            return False
        return True

    def _try_parse_date(self, value: Any) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if value in (None, ""):
            return None

        text = str(value).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    def _slug(self, text: str) -> str:
        text = str(text).strip().lower()
        replacements = {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
        }
        for source, target in replacements.items():
            text = text.replace(source, target)
        return text.replace(" ", "_")
