from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DashboardQuerySerializer, DashboardResponseSerializer
from .services import DashboardFilters, DashboardService


class DashboardOverviewAPIView(APIView):
    """
    GET /api/dashboard/overview/?start_date=2026-05-01&end_date=2026-05-31&statuses=Pendente,Confirmado
    """

    def get(self, request, *args, **kwargs):
        query_serializer = DashboardQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        filters = DashboardFilters(
            start_date=query_serializer.validated_data.get("start_date"),
            end_date=query_serializer.validated_data.get("end_date"),
            statuses=query_serializer.validated_data.get("statuses"),
        )

        service = DashboardService()
        payload = service.get_dashboard(filters)
        response_serializer = DashboardResponseSerializer(payload)
        return Response(response_serializer.data)
