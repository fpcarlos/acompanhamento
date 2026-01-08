from django.db import models
from django.conf import settings


class StatusPortariaFiscalizacao(models.Model):
    nome_status = models.CharField(max_length=80)
    sigla_status = models.CharField(max_length=80)
    ordem_exibicao = models.IntegerField()
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordem_exibicao']

    def __str__(self):
        return self.nome_status


class TipoFiscalizacao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()
    situacao_tipo_fiscalizacao = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class TipoPortaria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()
    situacao_tipo_portaria = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Entidade(models.Model):
    nome = models.CharField(max_length=255)
    sigla = models.CharField(max_length=50, blank=True)
    esfera = models.CharField(max_length=50, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        if self.sigla:
            return f"{self.nome} - {self.sigla}"
        return self.nome


class PortariaFiscalizacao(models.Model):
    numero_portaria = models.CharField(max_length=20, null=True, blank=True, unique=True)
    tipo_fiscalizacao = models.ForeignKey(TipoFiscalizacao, on_delete=models.PROTECT)
    tipo_portaria = models.ForeignKey(TipoPortaria, on_delete=models.PROTECT)
    numero_processo_sei = models.CharField(max_length=50)
    ano_processo_sei = models.CharField(max_length=4)
    objetivo = models.TextField()
    deliberacao = models.TextField()
    portaria_revogada = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT)
    entidades = models.ManyToManyField(Entidade, through='PortariaFiscalizacaoEntidade', blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    usuario_criacao = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='portarias_criadas', on_delete=models.PROTECT)
    usuario_atualizacao = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='portarias_atualizadas', on_delete=models.PROTECT)
    status_portaria = models.ForeignKey(StatusPortariaFiscalizacao, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        db_table = 'portaria_fiscalizacao'

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        # Ensure default status is 'EM_ELABORACAO' if available
        if self.status_portaria is None:
            try:
                default_status = StatusPortariaFiscalizacao.objects.get(sigla_status='EM_ELABORACAO')
                self.status_portaria = default_status
                super().save(update_fields=['status_portaria'])
            except StatusPortariaFiscalizacao.DoesNotExist:
                pass
        # Generate numero_portaria if missing (format: 0001/AAAA)
        if not self.numero_portaria and self.ano_processo_sei:
            self.numero_portaria = f"{self.id:04d}/{self.ano_processo_sei}"
            super().save(update_fields=['numero_portaria'])

    def __str__(self):
        return self.numero_portaria or f'Portaria {self.pk}'


class PortariaFiscalizacaoEntidade(models.Model):
    portaria = models.ForeignKey(PortariaFiscalizacao, on_delete=models.CASCADE)
    entidade = models.ForeignKey(Entidade, on_delete=models.PROTECT)
    data_vinculo = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portaria_fiscalizacao_entidade'

    def __str__(self):
        return f"{self.portaria} <-> {self.entidade}"
