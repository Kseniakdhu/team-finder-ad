from django.urls import path
from .views import ParticipantsListView, skills_autocomplete, AddSkillView, RemoveSkillView, RegisterView

urlpatterns = [
    path('list/', ParticipantsListView.as_view(), name='participants-list'),
    path('skills/', skills_autocomplete, name='skills-autocomplete'),
    path('<int:user_id>/skills/add', AddSkillView.as_view(), name='add-skill'),
    path('<int:user_id>/skills/<int:skill_id>/remove/', RemoveSkillView.as_view(), name='remove-skill'),
    path('register/', RegisterView.as_view(), name='register'),
]
