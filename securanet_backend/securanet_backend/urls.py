
# SecureNet-backend/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),              # Django admin
    path('', include('securanet.urls')),          # Main app routes
]

# ✅ Serve media files like screenshots in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
