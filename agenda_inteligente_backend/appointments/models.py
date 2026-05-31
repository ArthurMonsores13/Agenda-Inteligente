from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pendente", "Pendente"
        CONFIRMED = "Confirmado", "Confirmado"
        CANCELED = "Cancelado", "Cancelado"

    patient_name = models.CharField("nome do paciente", max_length=160)
    phone = models.CharField("telefone", max_length=40)
    appointment_date = models.DateField("data")
    appointment_time = models.TimeField("horario")
    service = models.CharField("servico", max_length=120, blank=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    cancellation_reason = models.TextField("motivo do cancelamento", blank=True)
    notes = models.TextField("observacoes", blank=True)
    finalized_at = models.DateTimeField("finalizado em", null=True, blank=True)
    finalized_synced_at = models.DateTimeField("finalizacao sincronizada em", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time", "patient_name"]
        indexes = [
            models.Index(fields=["appointment_date", "status"], name="appointmen_appoint_8bb80f_idx"),
            models.Index(fields=["status", "finalized_at"], name="appointmen_status_63b18b_idx"),
            models.Index(fields=["phone"], name="appointmen_phone_878438_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.patient_name} - {self.appointment_date} {self.appointment_time}"

    @property
    def appointment_datetime(self):
        value = datetime.combine(self.appointment_date, self.appointment_time)
        if timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def should_finalize(self) -> bool:
        if self.status != self.Status.CONFIRMED or self.finalized_at is not None:
            return False
        return self.appointment_datetime <= timezone.now() - timedelta(hours=24)
