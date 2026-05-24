from django.urls import path
from .views import ProjectListView, ProjectDetailView, CompleteProjectView, ToggleParticipateView

urlpatterns = [
    path('list/', ProjectListView.as_view(), name='project-list'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/complete/', CompleteProjectView.as_view(), name='project-complete'),
    path('<int:pk>/toggle-participate/', ToggleParticipateView.as_view(), name='project-toggle-participate'),
]
