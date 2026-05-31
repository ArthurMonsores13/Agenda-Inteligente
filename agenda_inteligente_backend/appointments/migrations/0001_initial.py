# Generated manually for the Agenda Inteligente MVP.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("patient_name", models.CharField(max_length=160, verbose_name="nome do paciente")),
                ("phone", models.CharField(max_length=40, verbose_name="telefone")),
                ("appointment_date", models.DateField(verbose_name="data")),
                ("appointment_time", models.TimeField(verbose_name="horario")),
                ("service", models.CharField(blank=True, max_length=120, verbose_name="servico")),
                (
                    "status",
                    models.CharField(
                        choices=[("Pendente", "Pendente"), ("Confirmado", "Confirmado"), ("Cancelado", "Cancelado")],
                        default="Pendente",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                ("cancellation_reason", models.TextField(blank=True, verbose_name="motivo do cancelamento")),
                ("notes", models.TextField(blank=True, verbose_name="observacoes")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["appointment_date", "appointment_time", "patient_name"],
            },
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["appointment_date", "status"], name="appointmen_appoint_8bb80f_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["phone"], name="appointmen_phone_878438_idx"),
        ),
    ]
