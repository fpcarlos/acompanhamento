from rest_framework.test import APIClient
from django.test import TestCase

from auditoria.models import Audit, Finding


class AuditoriaAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.audit = Audit.objects.create(title='APIAudit', description='API test')
        self.finding = Finding.objects.create(audit=self.audit, title='APIFind', severity='low')

    def test_list_audits(self):
        resp = self.client.get('/api/audits/')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert any(a['title'] == 'APIAudit' for a in data)

    def test_audit_detail_includes_findings(self):
        resp = self.client.get(f'/api/audits/{self.audit.pk}/')
        assert resp.status_code == 200
        data = resp.json()
        assert data['title'] == 'APIAudit'
        assert 'findings' in data
        assert isinstance(data['findings'], list)
        assert data['findings'][0]['title'] == 'APIFind'
