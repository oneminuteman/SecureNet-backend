from rest_framework import generics
from myapp.models import FileChangeLog
from myapp.serializers import FileChangeLogSerializer

class FileChangeLogListView(generics.ListAPIView):
    queryset = FileChangeLog.objects.all().order_by('-timestamp')
    serializer_class = FileChangeLogSerializer
