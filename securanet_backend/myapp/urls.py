from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'file-logs', views.FileChangeLogListView, basename='file-logs')

urlpatterns = [
    # No 'api/' prefix here - it's already added in the main urls.py
    path('', include(router.urls)),
    path('monitored-directories/', views.get_monitored_directories, name='monitored-directories'),
    path('statistics/', views.get_statistics, name='statistics'),
]