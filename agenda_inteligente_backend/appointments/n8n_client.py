from __future__ import annotations

from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen
import json
import logging
import os

from .models import Appointment


logger = logging.getLogger(__name__)


class N8nWebhookClient:
    def __init__(self) -> None:
        self.create_url = os.environ.get("N8N_WEBHOOK_APPOINTMENT_CREATE", "")
        self.update_url = os.environ.get("N8N_WEBHOOK_APPOINTMENT_UPDATE", "")
        self.delete_url = os.environ.get("N8N_WEBHOOK_APPOINTMENT_DELETE", "")
        self.finalize_url = os.environ.get("N8N_WEBHOOK_APPOINTMENT_FINALIZE", "")
        self.timeout = int(os.environ.get("N8N_WEBHOOK_TIMEOUT", "10"))

    def appointment_created(self, appointment: Appointment) -> None:
        self._post(self.create_url, self._appointment_payload(appointment, "created"))

    def appointment_updated(self, appointment: Appointment) -> None:
        self._post(self.update_url, self._appointment_payload(appointment, "updated"))

    def appointment_deleted(self, appointment: Appointment) -> None:
        self._post(self.delete_url, self._appointment_payload(appointment, "deleted"))

    def appointment_finalized(self, appointment: Appointment) -> None:
        self._post(self.finalize_url, self._appointment_payload(appointment, "finalized"))

    def _post(self, url: str, payload: dict[str, Any]) -> None:
        if not url:
            return

        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                response.read()
        except URLError:
            logger.exception("Falha ao enviar webhook para o n8n: %s", url)

    def _appointment_payload(self, appointment: Appointment, event: str) -> dict[str, Any]:
        return {
            "event": event,
            "appointment": {
                "id": appointment.id,
                "nome": appointment.patient_name,
                "telefone": appointment.phone,
                "data": appointment.appointment_date.isoformat(),
                "horario": appointment.appointment_time.strftime("%H:%M"),
                "servico": appointment.service,
                "status": appointment.status,
                "motivo_cancelamento": appointment.cancellation_reason,
                "observacoes": appointment.notes,
                "finalized_at": appointment.finalized_at.isoformat() if appointment.finalized_at else None,
                "created_at": appointment.created_at.isoformat() if appointment.created_at else None,
                "updated_at": appointment.updated_at.isoformat() if appointment.updated_at else None,
            },
        }
