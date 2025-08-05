
# SecureNet-backend/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/securanet/', include('securanet.urls')),
    path('api/myapp/', include('myapp.urls')),

    # Optional main route fallback (can be used for frontend rendering or redirection)
    path('', include('securanet.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
