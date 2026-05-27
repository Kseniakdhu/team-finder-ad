from django.contrib import admin

from projects.models import Skill


class SkillAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)
	list_filter = ("name",)


admin.site.register(Skill, SkillAdmin)
