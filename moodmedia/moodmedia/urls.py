from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
# moodmedia/urls.py

from django.conf.urls import handler404
from django.shortcuts import render


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),   # Add this
    path('accounts/', include('allauth.urls')),   # 👈 add this
    # ✅ built-in Django login/logout views
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
# Static/media file serving in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
handler404 = 'core.views.custom_404'