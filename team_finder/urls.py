from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
		path('admin/', admin.site.urls),
		path('projects/', include('projects.urls')),
		path('users/', include('users.urls')),
		path('', lambda request: redirect('project-list', permanent=False)),
]
