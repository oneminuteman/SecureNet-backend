from rest_framework import serializers
from myapp.models import FileChangeLog

class FileChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for FileChangeLog with AI analysis data"""
    
    # Add computed fields for better frontend display
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    
    # Extract key AI analysis fields for easier frontend access
    threats = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    risk_score = serializers.SerializerMethodField()
    
    class Meta:
        model = FileChangeLog
        fields = [
            'id',
            'dedup_key',
            'file_path',
            'change_type',
            'change_type_display',
            'risk_level',
            'risk_level_display',
            'recommendation',
            'ai_analysis',
            'file_size',
            'file_extension',
            'timestamp',
            'analyzed',
            'threats',
            'recommendations',
            'risk_score',
        ]
        read_only_fields = ['dedup_key', 'timestamp', 'ai_analysis']
    
    def get_threats(self, obj):
        """Extract threats from AI analysis"""
        if obj.ai_analysis and 'threats' in obj.ai_analysis:
            return obj.ai_analysis['threats']
        return []
    
    def get_recommendations(self, obj):
        """Extract recommendations from AI analysis"""
        if obj.ai_analysis and 'recommendations' in obj.ai_analysis:
            return obj.ai_analysis['recommendations']
        return []
    
    def get_risk_score(self, obj):
        """Extract risk score from AI analysis"""
        if obj.ai_analysis and 'risk_score' in obj.ai_analysis:
            return obj.ai_analysis['risk_score']
        return 0

class FileChangeLogSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    threat_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FileChangeLog
        fields = [
            'id',
            'file_path',
            'change_type',
            'change_type_display',
            'risk_level',
            'risk_level_display',
            'recommendation',
            'file_size',
            'file_extension',
            'timestamp',
            'analyzed',
            'threat_count',
        ]
    
    def get_threat_count(self, obj):
        """Get number of threats detected"""
        if obj.ai_analysis and 'threats' in obj.ai_analysis:
            return len(obj.ai_analysis['threats'])
        return 0

class SecurityDashboardSerializer(serializers.Serializer):
    """Serializer for security dashboard data"""
    
    monitor_status = serializers.DictField()
    statistics = serializers.DictField()
    recent_threats = serializers.ListField()
    security_summary = serializers.DictField()

class ThreatAnalysisSerializer(serializers.Serializer):
    """Serializer for threat analysis data"""
    
    threat_summary = serializers.DictField()
    recent_threats = serializers.ListField()
    total_threats = serializers.IntegerField()