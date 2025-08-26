from rest_framework import serializers
from .models import FileChangeLog, FileAnalysis

class FileAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAnalysis
        fields = ['id', 'file_path', 'content_hash', 'risk_score', 'risk_level', 'analysis_result', 'created_at']

class FileChangeLogSerializer(serializers.ModelSerializer):
    # Add metadata as a SerializerMethodField since it doesn't exist in the model
    metadata = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    analysis_data = serializers.SerializerMethodField()
    
    class Meta:
        model = FileChangeLog
        fields = ['id', 'file_path', 'file_name', 'change_type', 'timestamp', 
                  'risk_level', 'recommendation', 'metadata', 'analysis_data']
    
    def get_file_name(self, obj):
        """Extract just the filename from the full path"""
        import os
        return os.path.basename(obj.file_path)
    
    def get_metadata(self, obj):
        """Generate metadata about the file"""
        import os
        
        metadata = {
            'exists': False,
            'size': None,
            'last_modified': None,
            'is_directory': False,
            'extension': None
        }
        
        # Skip if the file was deleted
        if obj.change_type == 'deleted':
            return metadata
            
        try:
            if os.path.exists(obj.file_path):
                metadata['exists'] = True
                metadata['is_directory'] = os.path.isdir(obj.file_path)
                
                if not metadata['is_directory']:
                    stat = os.stat(obj.file_path)
                    metadata['size'] = stat.st_size
                    metadata['last_modified'] = stat.st_mtime
                    _, ext = os.path.splitext(obj.file_path)
                    metadata['extension'] = ext.lower() if ext else None
        except Exception:
            pass
            
        return metadata
    
    def get_analysis_data(self, obj):
        """Return analysis data if available"""
        if obj.analysis:
            return {
                'risk_score': obj.analysis.risk_score,
                'content_hash': obj.analysis.content_hash,
                'analysis_available': True
            }
        return {
            'analysis_available': False
        }

class FileChangeLogSummarySerializer(serializers.ModelSerializer):
    """A simplified serializer for list views"""
    file_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FileChangeLog
        fields = ['id', 'file_name', 'file_path', 'change_type', 'timestamp', 'risk_level']
    
    def get_file_name(self, obj):
        """Extract just the filename from the full path"""
        import os
        return os.path.basename(obj.file_path)