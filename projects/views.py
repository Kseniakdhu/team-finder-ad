from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, UpdateView

from common.constants import CLOSED_STATUS, OPEN_STATUS, PROJECTS_PAGINATE_BY
from projects.forms import ProjectForm
from projects.models import Project


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return redirect(reverse('projects:project-detail', args=[project.id]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Project, pk=self.kwargs.get(self.pk_url_kwarg))
        if obj.owner != self.request.user:
            raise PermissionDenied()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse('projects:project-detail', args=[self.object.id])


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']
    paginate_by = PROJECTS_PAGINATE_BY

    def get_queryset(self):
        return (
            Project.objects
            .select_related('owner')
            .prefetch_related('participants', 'skills', 'favorites')
            .annotate(participants_count=Count('participants'))
            .order_by('-created_at')
        )


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'


@method_decorator(login_required, name='dispatch')
class CompleteProjectView(View):

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user or project.status != OPEN_STATUS:
            return HttpResponseForbidden()
        project.status = CLOSED_STATUS
        project.save()
        return JsonResponse({"status": "ok", "project_status": CLOSED_STATUS})


@method_decorator(login_required, name='dispatch')
class ToggleParticipateView(View):

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        if user == project.owner:
            return HttpResponseForbidden()
        if (participant := project.participants.filter(pk=user.pk).exists()):
            project.participants.remove(user)
        else:
            project.participants.add(user)
        return JsonResponse({"status": "ok", "participant": participant})

