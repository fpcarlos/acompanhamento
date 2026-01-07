from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from paf.models import UnidadeTecnica, PAFAction


class PAFImportTests(TestCase):
    def setUp(self):
        UnidadeTecnica.objects.create(codigo='UT1', nome='Unidade 1')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user('tester', password='pwd')
        self.client.force_login(self.user)

    def test_upload_csv_valid_and_invalid_lines(self):
        csv_content = 'Código da Ação,Área de Atuação,Descrição da Ação,Unidade Técnica Responsável,Tipo de Produto / Instrumento,Indicador,Meta,Ano,Status\n'
        csv_content += 'PAF-2025-001,Area1,Desc,Unidade 1,Relatório,Indicador1,10,2025,VIGENTE\n'
        csv_content += 'PAF-2025-002,Area2,Desc2,Unidade X,Relatório,Ind2,not_a_number,2025,VIGENTE\n'
        f = SimpleUploadedFile('paf.csv', csv_content.encode('utf-8'), content_type='text/csv')
        resp = self.client.post(reverse('paf:paf-import'), {'file': f})
        self.assertEqual(resp.status_code, 302)
        # Check that one action was created and one failed
        self.assertEqual(PAFAction.objects.count(), 1)
