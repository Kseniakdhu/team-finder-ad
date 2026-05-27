import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from common.constants import PROJECTS_PAGINATE_BY, SKILLS_AUTOCOMPLETE_LIMIT
from projects.models import Skill
from users.forms import EditProfileForm, LoginForm, RegistrationForm
from users.models import User


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'


def logout_view(request):
    logout(request)
    return redirect('/projects/list/')


class ChangePasswordView(PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = 'users:user-details'

    def get_success_url(self):
        return reverse(self.success_url, kwargs={'user_id': self.request.user.id})


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = '/projects/list/'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Неверный email или пароль')
            return self.form_invalid(form)


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = RegistrationForm
    success_url = '/users/login/'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete_avatar'):
            user = request.user
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return redirect('users:edit-profile')
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.build_absolute_uri(
            reverse('users:user-details', kwargs={'user_id': self.request.user.id})
        )


@login_required
def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).order_by('name')[
        :SKILLS_AUTOCOMPLETE_LIMIT
    ]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@method_decorator(login_required, name='dispatch')
class AddSkillView(View):

    def post(self, request, user_id):
        if request.user.id != int(user_id):
            return HttpResponseForbidden()
        if request.content_type == "application/json":
            data = json.loads(request.body)
            skill_id = data.get('skill_id')
            name = data.get('name')
        else:
            skill_id = request.POST.get('skill_id')
            name = request.POST.get('name')
        created = False
        added = False
        skill = None
        if skill_id:
            skill = Skill.objects.filter(id=skill_id).first()
            if skill:
                if not request.user.skills.filter(id=skill.id).exists():
                    request.user.skills.add(skill)
                    added = True
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)
            if not request.user.skills.filter(id=skill.id).exists():
                request.user.skills.add(skill)
                added = True
        else:
            return HttpResponseBadRequest()
        return JsonResponse({
            "id": skill.id if skill else None,
            "name": skill.name if skill else None,
            "created": created,
            "added": added,
        })


@method_decorator(login_required, name='dispatch')
class RemoveSkillView(View):

    def post(self, request, user_id, skill_id):
        if request.user.id != int(user_id):
            return HttpResponseForbidden()
        skill = Skill.objects.filter(id=skill_id).first()
        if not skill or not request.user.skills.filter(id=skill.id).exists():
            return HttpResponseBadRequest()
        request.user.skills.remove(skill)
        return JsonResponse({"removed": True})


class ParticipantsListView(ListView):
    model = User
    template_name = 'users/participants.html'
    paginate_by = PROJECTS_PAGINATE_BY

    def get_queryset(self):
        skill_name = self.request.GET.get('skill')
        if skill_name:
            active_skill = Skill.objects.filter(name=skill_name).first()
            if active_skill:
                return User.objects.filter(skills=active_skill).order_by('-date_joined')
            return User.objects.none()
        return User.objects.all().order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill_name = self.request.GET.get('skill')
        all_skills = Skill.objects.filter(users__isnull=False).distinct()
        active_skill = (
            Skill.objects.filter(name=skill_name).first()
            if skill_name
            else None
        )
        query_prefix = f'skill={skill_name}&' if skill_name else ''
        context.update({
            'all_skills': all_skills,
            'active_skill': active_skill,
            'query_prefix': query_prefix,
        })
        return context
