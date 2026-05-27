from django import forms
from django.forms.widgets import ClearableFileInput

from users.models import User
from common.mixins import GithubUrlCleaner, PhoneCleaner
from users.avatar_utils import generate_avatar


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Старый пароль')
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Новый пароль')
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Повторите новый пароль')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Неверный старый пароль.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', 'Пароли не совпадают.')
        return cleaned_data


class RegistrationForm(PhoneCleaner, GithubUrlCleaner, forms.ModelForm):
    name = forms.CharField(label='Имя')
    surname = forms.CharField(label='Фамилия')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='Номер телефона')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'phone', 'avatar', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if not self.cleaned_data.get('avatar'):
            first_letter = self.cleaned_data.get('name', 'U')[0].upper()
            user.avatar = generate_avatar(first_letter)
        if commit:
            user.save()
        return user


class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = 'Удалить'
    initial_text = 'Текущий файл'
    input_text = 'Изменить'
    template_name = 'django/forms/widgets/clearable_file_input.html'


class EditProfileForm(PhoneCleaner, GithubUrlCleaner, forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'avatar': CustomClearableFileInput,
        }
        labels = {
            'avatar': 'Аватар',
        }


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
