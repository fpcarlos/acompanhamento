from rest_framework import viewsets, routers
from .models import Audit, Finding
from .serializers import AuditSerializer, FindingSerializer
from rest_framework.permissions import AllowAny


class AuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Audit.objects.all().order_by('-created_at')
    serializer_class = AuditSerializer
    permission_classes = [AllowAny]


class FindingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Finding.objects.all().order_by('-created_at')
    serializer_class = FindingSerializer
    permission_classes = [AllowAny]


router = routers.DefaultRouter()
router.register(r'audits', AuditViewSet, basename='audit')
router.register(r'findings', FindingViewSet, basename='finding')
