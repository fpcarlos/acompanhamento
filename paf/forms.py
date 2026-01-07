from django import forms


class PAFUploadForm(forms.Form):
    file = forms.FileField()
    replace_existing = forms.BooleanField(required=False, initial=False, help_text='Se marcado, substituirá o PAF do mesmo ano (se permitido)')
