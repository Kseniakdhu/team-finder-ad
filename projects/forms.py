from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    name = forms.CharField(label='Название проекта')
    description = forms.CharField(
        label='Описание проекта',
        widget=forms.Textarea,
        required=False)
    github_url = forms.URLField(label='Ссылка на GitHub', required=False)
    status = forms.ChoiceField(
        label='Статус', choices=[
            ('open', 'Открыт'), ('closed', 'Закрыт')])

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            from django.core.validators import URLValidator
            from django.core.exceptions import ValidationError
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise forms.ValidationError('Введите корректную ссылку.')
            if not (url.startswith('https://github.com/')
                    or url.startswith('http://github.com/')):
                raise forms.ValidationError(
                    'Ссылка должна вести на github.com')
        return url
