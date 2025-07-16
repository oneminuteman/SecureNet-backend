from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import FileChangeLog, FileAnalysis
from .serializers import FileChangeLogSerializer, FileChangeLogSummarySerializer
from .file_monitor.ai_analyzer.analyzer import SecurityAnalyzer
from rest_framework.decorators import action

class FileChangeLogListView(viewsets.ModelViewSet):
    queryset = FileChangeLog.objects.all().order_by('-timestamp')
    serializer_class = FileChangeLogSerializer  # Default serializer
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == 'list':
            return FileChangeLogSummarySerializer
        return FileChangeLogSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        file_log = self.get_object()
        analyzer = SecurityAnalyzer()
        
        try:
            with open(file_log.file_path, 'rb') as f:
                content = f.read()
            
            metadata = {
                'change_type': file_log.change_type,
                'timestamp': file_log.timestamp.isoformat(),
                'analyzed_by': request.user.username if request.user.is_authenticated else 'system'
            }
            
            result = analyzer.analyze_file(
                file_path=file_log.file_path,
                file_content=content,
                metadata=metadata
            )
            
            # Update the FileChangeLog with analysis results
            file_log.risk_level = result['risk_analysis']['risk_level']
            file_log.recommendation = result['recommendation']
            file_log.save()
            
            # Create or update FileAnalysis
            analysis, created = FileAnalysis.objects.update_or_create(
                file_path=file_log.file_path,
                defaults={
                    'content_hash': result['file_info']['hash'],
                    'risk_score': result['risk_analysis']['overall_score'],
                    'risk_level': result['risk_analysis']['risk_level'],
                    'analysis_result': result
                }
            )
            
            file_log.analysis = analysis
            file_log.save()
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': str(e),
                'status': 'failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)