from django.test import TestCase
from django.contrib.auth import get_user_model
from auditoria.models import Audit, Finding


class AuditModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('tester', password='pwd')

    def test_create_audit_and_finding(self):
        audit = Audit.objects.create(title='Revisão Contábil', description='Descrição', created_by=self.user)
        self.assertEqual(str(audit), 'Revisão Contábil (Aberto)')
        f = Finding.objects.create(audit=audit, title='Falta documentação', severity='high')
        self.assertEqual(f.audit, audit)
        self.assertFalse(f.resolved)


class AuditViewsTest(TestCase):
    def test_list_and_detail_view(self):
        audit = Audit.objects.create(title='Aud1')
        resp = self.client.get('/')
        self.assertContains(resp, 'Auditorias')
        resp2 = self.client.get(f'/audits/{audit.pk}/')
        self.assertContains(resp2, 'Aud1')
