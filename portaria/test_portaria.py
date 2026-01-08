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

    def test_entidade_search_endpoint(self):
        Entidade.objects.create(nome='Unidade ABC', sigla='UABC')
        Entidade.objects.create(nome='Outra Unidade', sigla='OU')
        resp = self.client.get(reverse('portaria:entidade-search'), {'q': 'Unidade'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        # should return at least one match
        self.assertTrue(len(data['results']) >= 1)
        # ensure results contain text and id
        item = data['results'][0]
        self.assertIn('id', item)
        self.assertIn('text', item)

    def test_list_filters(self):
        # prepare data
        tf1 = TipoFiscalizacao.objects.first()
        tp1 = TipoPortaria.objects.first()
        s1 = StatusPortariaFiscalizacao.objects.first()
        e1 = Entidade.objects.first()
        # create another tipo/status/entity
        tf2 = TipoFiscalizacao.objects.create(nome='Outra', descricao='')
        tp2 = TipoPortaria.objects.create(nome='Outra TP', descricao='')
        s2 = StatusPortariaFiscalizacao.objects.create(nome_status='Publicado', sigla_status='PORTARIA_PUBLICADA', ordem_exibicao=99)
        e2 = Entidade.objects.create(nome='Unidade Filter', sigla='UF')

        p1 = PortariaFiscalizacao.objects.create(tipo_fiscalizacao=tf1, tipo_portaria=tp1, numero_processo_sei='123', ano_processo_sei='2025', objetivo='BuscaFiltro', deliberacao='D', usuario_criacao=self.user, status_portaria=s1)
        p1.entidades.add(e1)
        p2 = PortariaFiscalizacao.objects.create(tipo_fiscalizacao=tf2, tipo_portaria=tp2, numero_processo_sei='999', ano_processo_sei='2025', objetivo='Outro', deliberacao='D', usuario_criacao=self.user, status_portaria=s2)
        p2.entidades.add(e2)

        # filter by tipo_fiscalizacao -> should show p1.number and not p2
        resp = self.client.get(reverse('portaria:portaria-list'), {'tipo_fiscalizacao': tf1.pk})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, p1.numero_portaria)
        self.assertNotContains(resp, p2.numero_portaria)

        # quick search by objective should return p1
        resp2 = self.client.get(reverse('portaria:portaria-list'), {'q': 'BuscaFiltro'})
        self.assertContains(resp2, p1.numero_portaria)

        # filter by entidade -> should show p2 only
        resp3 = self.client.get(reverse('portaria:portaria-list'), {'entidade': e2.pk})
        self.assertContains(resp3, p2.numero_portaria)
        self.assertNotContains(resp3, p1.numero_portaria)
