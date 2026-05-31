from django.contrib import admin
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok", "service": "agenda-inteligente-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckAPIView.as_view(), name="health-check"),
    path("api/appointments/", include("agenda_inteligente_backend.appointments.urls")),
    path("api/dashboard/", include("agenda_inteligente_backend.dashboard.urls")),
]
