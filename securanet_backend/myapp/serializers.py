from rest_framework import serializers
from myapp.models import FileChangeLog

class FileChangeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChangeLog
        fields = '__all__'