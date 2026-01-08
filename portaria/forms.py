from django import forms
from .models import PortariaFiscalizacao, Entidade


class PortariaForm(forms.ModelForm):
    entidades = forms.ModelMultipleChoiceField(queryset=Entidade.objects.filter(ativo=True), required=True)
    revoga_portaria = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = PortariaFiscalizacao
        fields = ['tipo_fiscalizacao', 'tipo_portaria', 'numero_processo_sei', 'ano_processo_sei', 'objetivo', 'deliberacao', 'portaria_revogada', 'entidades']

    def clean_objetivo(self):
        objetivo = self.cleaned_data.get('objetivo', '')
        if len(objetivo) < 10:
            raise forms.ValidationError('Objetivo deve ter pelo menos 10 caracteres')
        return objetivo

    def clean_deliberacao(self):
        deliberacao = self.cleaned_data.get('deliberacao', '')
        if len(deliberacao) < 10:
            raise forms.ValidationError('Deliberação deve ter pelo menos 10 caracteres')
        return deliberacao

    def clean(self):
        data = super().clean()
        revoga = data.get('revoga_portaria')
        portaria_revogada = data.get('portaria_revogada')
        if revoga and not portaria_revogada:
            raise forms.ValidationError('Você deve informar a portaria revogada')
        if portaria_revogada:
            # check not already revoked
            if portaria_revogada.status_portaria and portaria_revogada.status_portaria.sigla_status == 'PORTARIA_REVOGADA':
                raise forms.ValidationError('A portaria informada já está revogada')
        return data
