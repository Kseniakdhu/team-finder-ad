import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class PhoneCleaner:

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        normalized = self._normalize_phone(phone)
        if not normalized:
            raise forms.ValidationError(
                'Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
            )
        if self._phone_exists(normalized):
            raise forms.ValidationError(
                'Пользователь с таким номером телефона уже существует.'
            )
        return normalized

    def _normalize_phone(self, phone):
        phone = phone.replace(' ', '').replace('-', '')
        if re.fullmatch(r'8\d{10}', phone):
            return '+7' + phone[1:]
        if re.fullmatch(r'\+7\d{10}', phone):
            return phone
        return None

    def _phone_exists(self, normalized):
        model = getattr(self._meta, 'model', None)
        if not model:
            return False
        pk = getattr(self.instance, 'pk', None)
        return model.objects.exclude(pk=pk).filter(phone=normalized).exists()


class GithubUrlCleaner:
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise forms.ValidationError('Введите корректную ссылку.')
            if not (url.startswith('https://github.com/') or url.startswith('http://github.com/')):
                raise forms.ValidationError('Ссылка должна вести на github.com')
        return url
