from celery import shared_task
from .ai_analyzer.analyzer import AIFileAnalyzer
from ..models import FileChangeLog, FileAnalysis

@shared_task
def analyze_file_change(file_log_id):
    file_log = FileChangeLog.objects.get(id=file_log_id)
    
    analyzer = AIFileAnalyzer()
    
    with open(file_log.file_path, 'rb') as f:
        content = f.read()
    
    previous_changes = FileChangeLog.objects.filter(
        file_path=file_log.file_path
    ).order_by('-timestamp')[:10].values()
    
    metadata = {
        'change_type': file_log.change_type,
        'timestamp': file_log.timestamp.isoformat(),
        'previous_changes': list(previous_changes)
    }
    
    result = analyzer.analyze_file(
        file_path=file_log.file_path,
        file_content=content,
        metadata=metadata
    )
    
    analysis = FileAnalysis.objects.create(
        file_path=file_log.file_path,
        content_hash=result['file_info']['hash'],
        risk_score=result['risk_analysis']['overall_score'],
        risk_level=result['risk_analysis']['risk_level'],
        analysis_result=result
    )
    
    file_log.analysis = analysis
    file_log.save()
    
    return result