from django import forms
from .models import User

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Старый пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='Новый пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Повторите новый пароль')

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


class RegistrationForm(forms.ModelForm):
    name = forms.CharField(label='Имя')
    surname = forms.CharField(label='Фамилия')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(label='Номер телефона')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'phone', 'avatar', 'password']


    def clean_phone(self):
        phone = self.cleaned_data['phone']
        normalized = self._normalize_phone(phone)
        if not normalized:
            raise forms.ValidationError('Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX')
        # Проверка уникальности с учётом формата
        if User.objects.exclude(pk=self.instance.pk).filter(phone=normalized).exists():
            raise forms.ValidationError('Пользователь с таким номером телефона уже существует.')
        return normalized

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
            if not (url.startswith('https://github.com/') or url.startswith('http://github.com/')):
                raise forms.ValidationError('Ссылка должна вести на github.com')
        return url

    def _normalize_phone(self, phone):
        import re
        phone = phone.replace(' ', '').replace('-', '')
        if re.fullmatch(r'8\d{10}', phone):
            return '+7' + phone[1:]
        if re.fullmatch(r'\+7\d{10}', phone):
            return phone
        return None



class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']


    def clean_phone(self):
        phone = self.cleaned_data['phone']
        normalized = self._normalize_phone(phone)
        if not normalized:
            raise forms.ValidationError('Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX')
        # Проверка уникальности с учётом формата
        if User.objects.exclude(pk=self.instance.pk).filter(phone=normalized).exists():
            raise forms.ValidationError('Пользователь с таким номером телефона уже существует.')
        return normalized

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
            if not (url.startswith('https://github.com/') or url.startswith('http://github.com/')):
                raise forms.ValidationError('Ссылка должна вести на github.com')
        return url

    def _normalize_phone(self, phone):
        import re
        phone = phone.replace(' ', '').replace('-', '')
        if re.fullmatch(r'8\d{10}', phone):
            return '+7' + phone[1:]
        if re.fullmatch(r'\+7\d{10}', phone):
            return phone
        return None


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
