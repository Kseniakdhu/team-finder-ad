
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Project
from .forms import ProjectForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

class ProjectCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProjectForm()
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(reverse('project-detail', args=[project.id]))
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})

class ProjectEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return HttpResponseForbidden()
        form = ProjectForm(instance=project)
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return HttpResponseForbidden()
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(reverse('project-detail', args=[project.id]))
        return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})

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


@method_decorator(login_required, name='dispatch')
class ToggleFavoriteView(View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        if user in project.favorites.all():
            project.favorites.remove(user)
            is_favorite = False
        else:
            project.favorites.add(user)
            is_favorite = True
        return JsonResponse({"status": "ok", "is_favorite": is_favorite})
