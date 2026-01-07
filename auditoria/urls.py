from django.urls import path
from .views import AuditListView, AuditDetailView

app_name = 'auditoria'

urlpatterns = [
    path('', AuditListView.as_view(), name='audit-list'),
    path('audits/<int:pk>/', AuditDetailView.as_view(), name='audit-detail'),
]
