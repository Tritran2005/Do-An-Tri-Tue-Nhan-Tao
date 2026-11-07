"""
URL configuration for AI Recruitment Portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def root_redirect(request):
    """Trang chủ chuyển hướng: HR vào HR Dashboard, còn lại vào Sàn Việc Làm công khai."""
    if request.user.is_authenticated:
        if request.user.is_hr:
            return redirect('jobs:hr_dashboard')
    return redirect('jobs:job_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('', root_redirect, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
