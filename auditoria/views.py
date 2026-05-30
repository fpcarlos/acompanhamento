from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Audit


class AuditListView(LoginRequiredMixin, ListView):
    model = Audit
    template_name = 'auditoria/audit_list.html'
    context_object_name = 'audits'


class AuditDetailView(LoginRequiredMixin, DetailView):
    model = Audit
    template_name = 'auditoria/audit_detail.html'
    context_object_name = 'audit'
