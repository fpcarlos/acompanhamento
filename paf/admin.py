from django.contrib import admin
from .models import UnidadeTecnica, PAFAction, PAFImport


@admin.register(UnidadeTecnica)
class UnidadeTecnicaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome')
    search_fields = ('codigo', 'nome')


@admin.register(PAFAction)
class PAFActionAdmin(admin.ModelAdmin):
    list_display = ('codigo_acao', 'area_atuacao', 'unidade_tecnica', 'tipo_produto', 'indicador', 'meta', 'ano', 'status')
    list_filter = ('ano', 'status', 'tipo_produto')
    search_fields = ('codigo_acao', 'descricao', 'area_atuacao')


@admin.register(PAFImport)
class PAFImportAdmin(admin.ModelAdmin):
    list_display = ('file', 'year', 'uploaded_at', 'uploaded_by', 'processed')
    readonly_fields = ('uploaded_at',)
