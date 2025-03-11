from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/topics/', include('topics.urls')),
    path('api/teams/', include('teams.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)