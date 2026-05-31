from rest_framework import serializers

from .models import Appointment


def format_brazilian_phone(value: str) -> str:
    digits = "".join(char for char in str(value) if char.isdigit())
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return str(value).strip()


def only_phone_digits(value: str) -> str:
    return "".join(char for char in str(value) if char.isdigit())


class AppointmentSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source="patient_name", read_only=True)
    telefone = serializers.CharField(source="phone", read_only=True)
    data = serializers.DateField(source="appointment_date", read_only=True)
    horario = serializers.TimeField(source="appointment_time", read_only=True)
    servico = serializers.CharField(source="service", read_only=True)
    motivo_cancelamento = serializers.CharField(source="cancellation_reason", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "phone",
            "appointment_date",
            "appointment_time",
            "service",
            "status",
            "cancellation_reason",
            "notes",
            "finalized_at",
            "finalized_synced_at",
            "created_at",
            "updated_at",
            "nome",
            "telefone",
            "data",
            "horario",
            "servico",
            "motivo_cancelamento",
        ]
        read_only_fields = ["created_at", "updated_at", "finalized_at", "finalized_synced_at"]

    def validate_phone(self, value: str) -> str:
        return format_brazilian_phone(value)


class AppointmentWebhookSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    appointment_date = serializers.DateField(
        required=False,
        input_formats=["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"],
    )
    status = serializers.ChoiceField(choices=Appointment.Status.choices)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

    def to_internal_value(self, data):
        normalized = dict(data)
        aliases = {
            "id": "appointment_id",
            "telefone": "phone",
            "data": "appointment_date",
            "motivo_cancelamento": "cancellation_reason",
        }
        for source, target in aliases.items():
            if source in normalized and target not in normalized:
                normalized[target] = normalized[source]
        for key in ("appointment_date", "data", "phone", "telefone"):
            if normalized.get(key) == "":
                normalized.pop(key)
        return super().to_internal_value(normalized)

    def validate(self, attrs):
        if not attrs.get("appointment_id") and not attrs.get("phone"):
            raise serializers.ValidationError("Informe appointment_id ou phone.")
        return attrs
