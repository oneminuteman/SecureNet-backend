from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileChangeLogListView

router = DefaultRouter()
router.register(r'file-logs', FileChangeLogListView, basename='filelog')

urlpatterns = [
    path('', include(router.urls)),
]