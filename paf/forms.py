from django import forms


class PAFUploadForm(forms.Form):
    file = forms.FileField()
    replace_existing = forms.BooleanField(required=False, initial=False, help_text='Se marcado, substituirá o PAF do mesmo ano (se permitido)')


class ConfirmImportForm(forms.Form):
    import_id = forms.IntegerField(widget=forms.HiddenInput)
    replace_existing = forms.BooleanField(required=False, initial=False)
    confirm = forms.BooleanField(required=True, initial=True, widget=forms.HiddenInput)
