from django.db import migrations


def create_initial_data(apps, schema_editor):
    Status = apps.get_model('portaria', 'StatusPortariaFiscalizacao')
    TipoF = apps.get_model('portaria', 'TipoFiscalizacao')
    TipoP = apps.get_model('portaria', 'TipoPortaria')

    Status.objects.bulk_create([
        Status(nome_status='Em elaboração', sigla_status='EM_ELABORACAO', ordem_exibicao=1),
        Status(nome_status='Emissão autorizada / Aguardando assinatura', sigla_status='EMISSAO_AUTORIZADA_AGUARDANDO_ASSINATURA', ordem_exibicao=2),
        Status(nome_status='Emissão realizada / Aguardando publicação', sigla_status='EMISSAO_REALIZADA_AGUARDANDO_PUBLICACAO', ordem_exibicao=3),
        Status(nome_status='Portaria Cancelada', sigla_status='PORTARIA_CANCELADA', ordem_exibicao=4),
        Status(nome_status='Portaria Revogada', sigla_status='PORTARIA_REVOGADA', ordem_exibicao=5),
        Status(nome_status='Portaria publicada', sigla_status='PORTARIA_PUBLICADA', ordem_exibicao=6),
    ])

    TipoF.objects.bulk_create([
        TipoF(nome='Auditoria de Conformidade', descricao='Verificação da conformidade legal e regulamentar'),
        TipoF(nome='Auditoria Operacional', descricao='Avaliação da economicidade, eficiência e eficácia'),
        TipoF(nome='Inspeção', descricao='Levantamento de informações específicas'),
        TipoF(nome='Levantamento', descricao='Identificação de objetos e instrumentos de fiscalização'),
        TipoF(nome='Monitoramento', descricao='Acompanhamento de implementação de determinações'),
        TipoF(nome='Acompanhamento', descricao='Monitoramento em tempo real da execução visando assegurar a eficiência, a transparência e a rastreabilidade dessas ações de controle'),
    ])

    TipoP.objects.bulk_create([
        TipoP(nome='Portaria de Constituição de Equipe', descricao='Designa equipe para trabalho de fiscalização'),
        TipoP(nome='Portaria de Designação', descricao='Designa servidor para atividade específica'),
        TipoP(nome='Portaria de Prorrogação', descricao='Prorroga prazo de portaria anterior'),
        TipoP(nome='Portaria de Substituição', descricao='Substitui membro da equipe'),
        TipoP(nome='Portaria de Planejamento', descricao='Etapa de planejamento'),
        TipoP(nome='Portaria de Execução e Relatório', descricao='Etapa de execução e relatório'),
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('portaria', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]
