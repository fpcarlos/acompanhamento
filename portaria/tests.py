from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from .models import TipoFiscalizacao, TipoPortaria, StatusPortariaFiscalizacao, Entidade, PortariaFiscalizacao


class PortariaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('tester', password='pwd')
        self.client.force_login(self.user)
        # initial data
        if not StatusPortariaFiscalizacao.objects.filter(sigla_status='EM_ELABORACAO').exists():
            StatusPortariaFiscalizacao.objects.create(nome_status='Em elaboração', sigla_status='EM_ELABORACAO', ordem_exibicao=1)
        if not TipoFiscalizacao.objects.filter(nome='Auditoria de Conformidade').exists():
            TipoFiscalizacao.objects.create(nome='Auditoria de Conformidade', descricao='')
        if not TipoPortaria.objects.filter(nome='Portaria de Constituição de Equipe').exists():
            TipoPortaria.objects.create(nome='Portaria de Constituição de Equipe', descricao='')
        if not Entidade.objects.filter(nome='Unidade X').exists():
            Entidade.objects.create(nome='Unidade X', sigla='UX')

    def test_create_portaria_defaults(self):
        tipo_f = TipoFiscalizacao.objects.first()
        tipo_p = TipoPortaria.objects.first()
        entidade = Entidade.objects.first()
        resp = self.client.post(reverse('portaria:portaria-create'), {
            'tipo_fiscalizacao': tipo_f.pk,
            'tipo_portaria': tipo_p.pk,
            'numero_processo_sei': '12345',
            'ano_processo_sei': '2025',
            'objetivo': 'Objetivo com mais de dez chars',
            'deliberacao': 'Deliberação detalhada aqui',
            'entidades': [entidade.pk],
        })
        # redirect to detail
        self.assertEqual(resp.status_code, 302)
        p = PortariaFiscalizacao.objects.first()
        self.assertIsNotNone(p.numero_portaria)
        self.assertEqual(p.status_portaria.sigla_status, 'EM_ELABORACAO')
