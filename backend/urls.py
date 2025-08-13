from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('sms.urls')),  # Replace 'sms' with your actual app name if different
]
