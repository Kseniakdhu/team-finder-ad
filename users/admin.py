from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'avatar', 'phone', 'github_url', 'about')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'avatar', 'phone', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name', 'surname', 'is_staff')
    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
