from django.utils import timezone

from .models import Appointment
from .n8n_client import N8nWebhookClient


class AppointmentFinalizationService:
    def __init__(self, n8n_client: N8nWebhookClient | None = None) -> None:
        self.n8n_client = n8n_client or N8nWebhookClient()

    def finalize_due_appointments(self) -> int:
        finalized_count = 0
        candidates = Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED,
            finalized_at__isnull=True,
        )

        for appointment in candidates:
            if not appointment.should_finalize():
                continue
            appointment.finalized_at = timezone.now()
            appointment.save(update_fields=["finalized_at", "updated_at"])
            self.n8n_client.appointment_finalized(appointment)
            appointment.finalized_synced_at = timezone.now()
            appointment.save(update_fields=["finalized_synced_at", "updated_at"])
            finalized_count += 1

        return finalized_count
