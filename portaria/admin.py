from django.contrib import admin
from . import models


@admin.register(models.StatusPortariaFiscalizacao)
class StatusPortariaAdmin(admin.ModelAdmin):
    list_display = ('nome_status', 'sigla_status', 'ordem_exibicao', 'ativo')


@admin.register(models.TipoFiscalizacao)
class TipoFiscalizacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'situacao_tipo_fiscalizacao')


@admin.register(models.TipoPortaria)
class TipoPortariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'situacao_tipo_portaria')


@admin.register(models.Entidade)
class EntidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'esfera', 'ativo')
    search_fields = ('nome', 'sigla')


@admin.register(models.PortariaFiscalizacao)
class PortariaFiscalizacaoAdmin(admin.ModelAdmin):
    list_display = ('numero_portaria', 'tipo_fiscalizacao', 'tipo_portaria', 'data_criacao', 'status_portaria')
    readonly_fields = ('numero_portaria', 'data_criacao', 'data_atualizacao')


@admin.register(models.PortariaFiscalizacaoEntidade)
class PortariaFiscalizacaoEntidadeAdmin(admin.ModelAdmin):
    list_display = ('portaria', 'entidade', 'data_vinculo')
