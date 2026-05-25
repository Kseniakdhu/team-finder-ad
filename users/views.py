from django.contrib.auth import authenticate, logout, login, update_session_auth_hash
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import User
from projects.models import Skill
from .forms import RegistrationForm, EditProfileForm, LoginForm, ChangePasswordForm


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
            return redirect('user-details', user_id=request.user.id)
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
                return redirect('project-list')
            else:
                form.add_error(None, 'Неверный email или пароль')
        return render(request, 'users/login.html', {'form': form})
    
class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # После регистрации не логиним пользователя, а перенаправляем на страницу входа
            return redirect('users:login')
        return render(request, 'users/register.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-details', user_id=request.user.id)
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
        if request.user.id != int(user_id):
            return HttpResponseForbidden()
        skill_id = request.POST.get('skill_id')
        name = request.POST.get('name')
        created = False
        added = False
        if skill_id:
            skill = Skill.objects.filter(id=skill_id).first()
            if skill and not request.user.skills.filter(id=skill.id).exists():
                request.user.skills.add(skill)
                added = True
        elif name:
            skill, created = Skill.objects.get_or_create(name=name)
            if not request.user.skills.filter(id=skill.id).exists():
                request.user.skills.add(skill)
                added = True
        else:
            return HttpResponseBadRequest()
        return JsonResponse({"skill_id": skill.id if skill else None, "created": created, "added": added})


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
        skill_name = request.GET.get('skill')
        all_skills = Skill.objects.all()
        active_skill = None
        if skill_name:
            active_skill = Skill.objects.filter(name=skill_name).first()
            if active_skill:
                participants = User.objects.filter(skills=active_skill).order_by('id')
            else:
                participants = User.objects.none()
        else:
            participants = User.objects.all().order_by('id')
        return render(request, 'users/participants.html', {
            'participants': participants,
            'all_skills': all_skills,
            'active_skill': active_skill,
        })
