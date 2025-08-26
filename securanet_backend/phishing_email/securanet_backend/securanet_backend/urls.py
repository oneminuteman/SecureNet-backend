# SecureNet-backend/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# drf-yasg imports for API documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    path('api/', include('phishing_detection.urls')),       # API routes for phishing detection app
    path('', include('securanet.urls')),                    # Root goes to securanet

    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
