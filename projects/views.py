
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Project

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']

    def get_queryset(self):
        return Project.objects.all().order_by('-created_at')


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'


@method_decorator(login_required, name='dispatch')
class CompleteProjectView(View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user or project.status != 'open':
            return HttpResponseForbidden()
        project.status = 'closed'
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})


@method_decorator(login_required, name='dispatch')
class ToggleParticipateView(View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        if user == project.owner:
            return HttpResponseForbidden()
        if user in project.participants.all():
            project.participants.remove(user)
            participated = False
        else:
            project.participants.add(user)
            participated = True
        return JsonResponse({"status": "ok", "participated": participated})
