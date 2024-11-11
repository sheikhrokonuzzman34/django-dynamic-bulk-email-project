from django import forms
from main.models import *

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10}),
        }

class BulkEmailForm(forms.Form):
    template = forms.ModelChoiceField(queryset=EmailTemplate.objects.all())
    excel_file = forms.FileField(help_text='Upload Excel file with columns: name, email')