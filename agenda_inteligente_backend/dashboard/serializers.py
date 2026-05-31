from rest_framework import serializers


class DashboardQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    statuses = serializers.CharField(required=False)

    def validate_statuses(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]


class DashboardResponseSerializer(serializers.Serializer):
    summary = serializers.CharField()
    metrics = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    charts = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    column_profiles = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    filters = serializers.DictField()
    metadata = serializers.DictField()
