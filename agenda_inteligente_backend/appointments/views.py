from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .finalization import AppointmentFinalizationService
from .models import Appointment
from .n8n_client import N8nWebhookClient
from .serializers import AppointmentSerializer, AppointmentWebhookSerializer, only_phone_digits


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    n8n_client_class = N8nWebhookClient
    finalization_service_class = AppointmentFinalizationService

    def get_queryset(self) -> QuerySet[Appointment]:
        self.finalization_service_class().finalize_due_appointments()
        queryset = super().get_queryset()
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        statuses = self.request.query_params.get("statuses")
        scope = self.request.query_params.get("scope", "active")

        if scope == "finalized":
            queryset = queryset.filter(finalized_at__isnull=False)
        elif scope == "all":
            queryset = queryset
        else:
            queryset = queryset.filter(finalized_at__isnull=True)

        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        if statuses:
            queryset = queryset.filter(status__in=[item.strip() for item in statuses.split(",") if item.strip()])

        return queryset

    def perform_create(self, serializer):
        appointment = serializer.save()
        self.n8n_client_class().appointment_created(appointment)

    def perform_update(self, serializer):
        appointment = serializer.save()
        if appointment.status != Appointment.Status.CONFIRMED and appointment.finalized_at is not None:
            appointment.finalized_at = None
            appointment.finalized_synced_at = None
            appointment.save(update_fields=["finalized_at", "finalized_synced_at", "updated_at"])
        self.n8n_client_class().appointment_updated(appointment)

    def perform_destroy(self, instance):
        self.n8n_client_class().appointment_deleted(instance)
        instance.delete()

    @action(detail=False, methods=["post"], url_path="webhook/status")
    def webhook_status(self, request):
        serializer = AppointmentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        appointment = self._find_webhook_appointment(data)
        if appointment is None:
            return Response(
                {"detail": "Agendamento nao encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        appointment.status = data["status"]
        if data.get("cancellation_reason") is not None:
            appointment.cancellation_reason = data.get("cancellation_reason", "")
        if appointment.status != Appointment.Status.CONFIRMED:
            appointment.finalized_at = None
            appointment.finalized_synced_at = None
        appointment.save(update_fields=["status", "cancellation_reason", "finalized_at", "finalized_synced_at", "updated_at"])
        self.n8n_client_class().appointment_updated(appointment)

        return Response(AppointmentSerializer(appointment).data)

    def _find_webhook_appointment(self, data: dict) -> Appointment | None:
        if data.get("appointment_id"):
            return Appointment.objects.filter(id=data["appointment_id"]).first()

        target_phone = only_phone_digits(data.get("phone", ""))
        queryset = Appointment.objects.all()
        if target_phone:
            queryset = [
                appointment
                for appointment in queryset
                if only_phone_digits(appointment.phone) == target_phone
            ]
        else:
            queryset = []

        if data.get("appointment_date"):
            queryset = [
                appointment
                for appointment in queryset
                if appointment.appointment_date == data["appointment_date"]
            ]
        return sorted(queryset, key=lambda item: (item.appointment_date, item.appointment_time))[0] if queryset else None
