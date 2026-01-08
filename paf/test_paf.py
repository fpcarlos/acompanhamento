from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from paf.models import UnidadeTecnica, PAFAction, PAFImport


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
        # Initial upload should render preview page (status 200)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('preview_rows', resp.context)
        imp = resp.context['import']
        # Confirm import
        resp2 = self.client.post(reverse('paf:paf-import'), {'import_id': imp.id, 'confirm': 'true'})
        self.assertEqual(resp2.status_code, 302)
        # Check that one action was created and one failed
        self.assertEqual(PAFAction.objects.count(), 1)
        # Check that an import record was created and has summary with one error
        from paf.models import PAFImport
        self.assertTrue(PAFImport.objects.exists())
        pi = PAFImport.objects.first()
        self.assertTrue(pi.summary)
        self.assertEqual(pi.summary.get('processed'), 1)
        self.assertEqual(len(pi.summary.get('errors', [])), 1)

    def test_upload_csv_with_unidade_codigo(self):
        # Ensure importer matches unidade by codigo
        csv_content = 'Código da Ação,Área de Atuação,Descrição da Ação,Unidade Técnica Responsável,Tipo de Produto / Instrumento,Indicador,Meta,Ano,Status\n'
        csv_content += 'PAF-2025-010,Area1,Desc,UT1,Relatório,Indicador1,10,2025,VIGENTE\n'
        f = SimpleUploadedFile('paf2.csv', csv_content.encode('utf-8'), content_type='text/csv')
        resp = self.client.post(reverse('paf:paf-import'), {'file': f})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('preview_rows', resp.context)
        imp = resp.context['import']
        resp2 = self.client.post(reverse('paf:paf-import'), {'import_id': imp.id, 'confirm': 'true'})
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(PAFAction.objects.filter(codigo_acao='PAF-2025-010').exists())
        pi = PAFImport.objects.order_by('-uploaded_at').first()
        self.assertEqual(pi.summary.get('processed'), 1)

    def test_preview_and_confirm_import(self):
        csv_content = 'Código da Ação,Área de Atuação,Descrição da Ação,Unidade Técnica Responsável,Tipo de Produto / Instrumento,Indicador,Meta,Ano,Status\n'
        csv_content += 'PAF-2025-020,Area1,Desc,Unidade 1,Relatório,Indicador1,10,2025,VIGENTE\n'
        f = SimpleUploadedFile('paf_preview.csv', csv_content.encode('utf-8'), content_type='text/csv')
        resp = self.client.post(reverse('paf:paf-import'), {'file': f})
        # Should render preview page (status 200)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('preview_rows', resp.context)
        imp = resp.context['import']
        # Now confirm import
        resp2 = self.client.post(reverse('paf:paf-import'), {'import_id': imp.id, 'confirm': 'true'})
        self.assertEqual(resp2.status_code, 302)
        self.assertTrue(PAFAction.objects.filter(codigo_acao='PAF-2025-020').exists())

    def test_replace_blocked_when_in_execution(self):
        # Create existing action in EM_EXECUCAO
        ut = UnidadeTecnica.objects.first()
        from paf.models import PAFAction
        PAFAction.objects.create(codigo_acao='PAF-2026-001', area_atuacao='A', descricao='D', unidade_tecnica=ut, tipo_produto='T', indicador='I', meta='1', ano=2026, status=PAFAction.Status.EM_EXECUCAO)
        csv_content = 'Código da Ação,Área de Atuação,Descrição da Ação,Unidade Técnica Responsável,Tipo de Produto / Instrumento,Indicador,Meta,Ano,Status\n'
        csv_content += 'PAF-2026-002,Area1,Desc,Unidade 1,Relatório,Indicador1,10,2026,VIGENTE\n'
        f = SimpleUploadedFile('paf_replace.csv', csv_content.encode('utf-8'), content_type='text/csv')
        # Upload and preview
        resp = self.client.post(reverse('paf:paf-import'), {'file': f, 'replace_existing': 'on'})
        self.assertEqual(resp.status_code, 200)
        imp = resp.context['import']
        # Confirm with replace flag
        resp2 = self.client.post(reverse('paf:paf-import'), {'import_id': imp.id, 'confirm': 'true', 'replace_existing': 'on'})
        # Should redirect and create an import summary with error
        from paf.models import PAFImport
        pi = PAFImport.objects.filter(pk=imp.id).first()
        self.assertTrue('Não é possível substituir' in pi.summary.get('errors')[0]['error'])
