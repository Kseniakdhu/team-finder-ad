from django.urls import path

from users.views import (
    ParticipantsListView,
    skills_autocomplete,
    AddSkillView,
    RemoveSkillView,
    RegisterView,
    EditProfileView,
    LoginView,
    ChangePasswordView,
    logout_view,
    UserDetailView,
)

urlpatterns = [
    path(
        'list/',
        ParticipantsListView.as_view(),
        name='participants-list'),
    path(
        '<int:user_id>/',
        UserDetailView.as_view(),
        name='user-details'),
    path(
        'skills/',
        skills_autocomplete,
        name='skills-autocomplete'),
    path(
        '<int:user_id>/skills/add/',
        AddSkillView.as_view(),
        name='add-skill'),
    path(
        '<int:user_id>/skills/<int:skill_id>/remove/',
        RemoveSkillView.as_view(),
        name='remove-skill'),
    path(
        'register/',
        RegisterView.as_view(),
        name='register'),
    path(
        'edit_profile/',
        EditProfileView.as_view(),
        name='edit-profile'),
    path(
        'login/',
        LoginView.as_view(),
        name='login'),
    path(
        'change_password/',
        ChangePasswordView.as_view(),
        name='change-password'),
    path(
        'logout/',
        logout_view,
        name='logout'),
]
