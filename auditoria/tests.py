from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Audit, Finding

User = get_user_model()


class AuditModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='testpwd123')

    def test_create_audit_and_finding(self):
        audit = Audit.objects.create(title='Revisão Contábil', description='Descrição', created_by=self.user)
        self.assertEqual(str(audit), 'Revisão Contábil (Aberto)')
        f = Finding.objects.create(audit=audit, title='Falta documentação', severity='high')
        self.assertEqual(f.audit, audit)
        self.assertFalse(f.resolved)


class AuditViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('viewer', password='testpwd123')

    def test_anonymous_is_redirected(self):
        """Views must require authentication."""
        audit = Audit.objects.create(title='Aud1')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        resp2 = self.client.get(f'/audits/{audit.pk}/')
        self.assertEqual(resp2.status_code, 302)

    def test_list_and_detail_view(self):
        self.client.force_login(self.user)
        audit = Audit.objects.create(title='Aud1')
        resp = self.client.get('/')
        self.assertContains(resp, 'Auditorias')
        resp2 = self.client.get(f'/audits/{audit.pk}/')
        self.assertContains(resp2, 'Aud1')
