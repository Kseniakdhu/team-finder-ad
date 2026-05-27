from django.urls import path

from projects.views import (
    CompleteProjectView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectEditView,
    ProjectListView,
    ToggleParticipateView,
)

app_name = 'projects'

urlpatterns = [
    path(
        'list/',
        ProjectListView.as_view(),
        name='project-list'),
    path(
        '<int:pk>/',
        ProjectDetailView.as_view(),
        name='project-detail'),
    path(
        '<int:pk>/complete/',
        CompleteProjectView.as_view(),
        name='project-complete'),
    path(
        '<int:pk>/toggle-participate/',
        ToggleParticipateView.as_view(),
        name='project-toggle-participate'),
    path(
        'create-project/',
        ProjectCreateView.as_view(),
        name='project-create'),
    path(
        '<int:pk>/edit/',
        ProjectEditView.as_view(),
        name='project-edit'),
]
