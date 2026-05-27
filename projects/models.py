from django.conf import settings
from django.db import models
from django.urls import reverse

from common.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    OPEN_STATUS,
    CLOSED_STATUS,
)


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        (OPEN_STATUS, 'Open'),
        (CLOSED_STATUS, 'Closed'),
    ]

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owned_projects',
        on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=OPEN_STATUS)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True)
    skills = models.ManyToManyField(Skill, related_name='projects', blank=True)
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_projects',
        blank=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id)])
