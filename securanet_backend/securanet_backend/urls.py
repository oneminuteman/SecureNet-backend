# SecureNet-backend/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# drf-yasg imports for API documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ✅ Import get_csrf_token view (adjust app name if needed)
from securanet.views import get_csrf_token   # <-- if it's in securanet app
# from file_management.views import get_csrf_token  # <-- use this if it's inside file_management app

# API Documentation schema
schema_view = get_schema_view(
    openapi.Info(
        title="SecuraNet API",
        default_version='v1',
        description="API documentation for the SecuraNet project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),                        # Django admin
    path('api/', include('securanet.urls')),                # API routes for securanet app
    path('api/file-management/', include('file_management.urls')),
    # path('api/', include('phishing_detection.urls')),       # API routes for phishing detection app
    path('', include('securanet.urls')),                    # Root goes to securanet
    path("api/get-csrf/", get_csrf_token, name="get_csrf"), # ✅ CSRF endpoint

    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

