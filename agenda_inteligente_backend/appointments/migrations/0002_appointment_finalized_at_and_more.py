# Generated manually for automatic appointment finalization.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="finalized_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="finalizado em"),
        ),
        migrations.AddField(
            model_name="appointment",
            name="finalized_synced_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="finalizacao sincronizada em"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["status", "finalized_at"], name="appointmen_status_63b18b_idx"),
        ),
    ]
