from rest_framework import serializers
from .models import FileChangeLog, FileAnalysis

class FileAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAnalysis
        fields = ['file_path', 'content_hash', 'risk_score', 'risk_level', 'analysis_result', 'created_at']

class FileChangeLogSerializer(serializers.ModelSerializer):
    analysis = FileAnalysisSerializer(read_only=True)

    class Meta:
        model = FileChangeLog
        fields = [
            'id',
            'file_path',
            'change_type',
            'timestamp',
            'analysis',
            'metadata',
            'dedup_key',
            'recommendation',
            'risk_level'
        ]

class FileChangeLogSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = FileChangeLog
        fields = [
            'id',
            'file_path',
            'change_type',
            'timestamp',
            'risk_level',
            'recommendation'
        ]