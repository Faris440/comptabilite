from django import forms
import os.path
class SomeImportForm(forms.Form):
    import_file = forms.FileField(label="Select file to import")
    """format = forms.ChoiceField(
        choices=[(i, fmt().get_title()) for i, fmt in enumerate(get_import_formats())],
        label="File format"
    )"""

class ConfirmImportForm(forms.Form):
    import_file_name = forms.CharField(widget=forms.HiddenInput())
    original_file_name = forms.CharField(widget=forms.HiddenInput())
    format = forms.CharField(widget=forms.HiddenInput())
    resource = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_import_file_name(self):
        data = self.cleaned_data["import_file_name"]
        data = os.path.basename(data)
        return data
