from rest_framework import serializers
from .models import PhishingLog

class PhishingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhishingLog
        fields = '__all__'
