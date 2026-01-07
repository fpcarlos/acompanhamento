from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UnidadeTecnica(models.Model):
    """Represents a technical unit that can be referenced by PAF actions."""
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class PAFAction(models.Model):
    class Status(models.TextChoices):
        VIGENTE = 'VIGENTE', _('Vigente')
        EM_EXECUCAO = 'EM_EXECUCAO', _('Em Execução')
        CONCLUIDO = 'CONCLUIDO', _('Concluído')

    codigo_acao = models.CharField(max_length=30)
    area_atuacao = models.CharField(max_length=250)
    descricao = models.TextField()
    unidade_tecnica = models.ForeignKey(UnidadeTecnica, on_delete=models.PROTECT, related_name='paf_actions')
    tipo_produto = models.CharField(max_length=250)
    indicador = models.CharField(max_length=250)
    meta = models.CharField(max_length=250)
    ano = models.IntegerField()
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.VIGENTE)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('codigo_acao', 'ano')

    def __str__(self):
        return f"{self.codigo_acao} ({self.ano})"


class PAFImport(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='paf_imports/')
    year = models.IntegerField()
    processed = models.BooleanField(default=False)
    summary = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"PAFImport {self.file.name} ({self.year})"
