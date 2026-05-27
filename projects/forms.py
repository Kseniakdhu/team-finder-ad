from django import forms

from projects.models import Project
from common.mixins import GithubUrlCleaner


class ProjectForm(GithubUrlCleaner, forms.ModelForm):
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
