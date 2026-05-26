from django.contrib.auth import (
    authenticate, logout, login, update_session_auth_hash
)
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.http import (
    JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import User
from projects.models import Skill
from .forms import (
    RegistrationForm, EditProfileForm, LoginForm, ChangePasswordForm
)


class UserDetailView(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return render(request, 'users/user-details.html', {'user': user})


def logout_view(request):
    logout(request)
    return redirect('/projects/list/')


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    def get(self, request):
        form = ChangePasswordForm(user=request.user)
        return render(request, 'users/change_password.html', {'form': form})

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            return redirect('users:user-details', user_id=request.user.id)
        return render(request, 'users/change_password.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('projects:project-list')
            else:
                form.add_error(None, 'Неверный email или пароль')
        return render(request, 'users/login.html', {'form': form})


class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('users:login')
        return render(request, 'users/register.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        if request.POST.get('delete_avatar'):
            user = request.user
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return redirect('users:edit-profile')
        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:user-details', user_id=request.user.id)
        return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@method_decorator(login_required, name='dispatch')
class AddSkillView(View):
    def post(self, request, user_id):
        import json
        if request.user.id != int(user_id):
            return HttpResponseForbidden()
        # Поддержка JSON-запроса от JS
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
        # Возвращаем id и name для JS
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


class ParticipantsListView(View):
    def get(self, request):
        from django.core.paginator import Paginator
        skill_name = request.GET.get('skill')
        all_skills = Skill.objects.filter(users__isnull=False).distinct()
        active_skill = None
        if skill_name:
            active_skill = Skill.objects.filter(name=skill_name).first()
            if active_skill:
                users_qs = User.objects.filter(
                    skills=active_skill).order_by('-date_joined')
            else:
                users_qs = User.objects.none()
        else:
            users_qs = User.objects.all().order_by('-date_joined')

        paginator = Paginator(users_qs, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Для корректной работы пагинации с фильтрами
        query_prefix = ''
        if skill_name:
            query_prefix = f'skill={skill_name}&'

        return render(request, 'users/participants.html', {
            'page_obj': page_obj,
            'all_skills': all_skills,
            'active_skill': active_skill,
            'query_prefix': query_prefix,
        })
