from django.urls import path
from .views import FileChangeLogListView

urlpatterns = [
    path('file-logs/', FileChangeLogListView.as_view(), name='file-logs'),
]
