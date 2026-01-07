from rest_framework import serializers
from .models import Audit, Finding


class FindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finding
        fields = ('id', 'title', 'description', 'severity', 'resolved', 'created_at')


class AuditSerializer(serializers.ModelSerializer):
    findings = FindingSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Audit
        fields = ('id', 'title', 'description', 'status', 'created_by', 'created_at', 'updated_at', 'findings')

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None
