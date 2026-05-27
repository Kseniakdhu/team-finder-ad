from django.contrib.auth.models import BaseUserManager

from users.avatar_utils import generate_avatar


class UserManager(BaseUserManager):

    def create_user(
            self,
            email,
            name,
            surname,
            phone,
            avatar=None,
            password=None,
            **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        if not avatar:
            first_letter = name[0].upper() if name else 'U'
            avatar = generate_avatar(first_letter)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone,
            avatar=avatar,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email,
            name,
            surname,
            phone,
            avatar,
            password=None,
            **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            email,
            name,
            surname,
            phone,
            avatar,
            password,
            **extra_fields)
