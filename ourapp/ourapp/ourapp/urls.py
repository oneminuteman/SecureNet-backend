"""
URL configuration for the integrated security platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("<h1>SecureNet Integrated Security Platform</h1><p>Combined file monitoring and clone detection</p>")

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('websec/', include('securanet.urls')),
]

# Add media URLs for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)