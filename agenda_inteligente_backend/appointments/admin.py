from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "appointment_date", "appointment_time", "service", "status", "phone")
    list_filter = ("status", "appointment_date", "service")
    search_fields = ("patient_name", "phone", "service")
