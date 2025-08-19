from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import FileChangeLog, FileAnalysis
from .serializers import FileChangeLogSerializer, FileChangeLogSummarySerializer
import os
import json
from django.conf import settings
import time
import logging
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.cache import never_cache
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
import subprocess
import sys
from .file_monitor.watcher import get_monitor_thread, stop_monitor, ensure_single_monitor

logger = logging.getLogger(__name__)

class FileChangeLogListView(viewsets.ModelViewSet):
    queryset = FileChangeLog.objects.all().order_by('-timestamp')
    serializer_class = FileChangeLogSerializer

    class StandardResultsSetPagination(PageNumberPagination):
        page_size = 50
        page_size_query_param = 'page_size'
        max_page_size = 100
    
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == 'list':
            return FileChangeLogSummarySerializer
        return FileChangeLogSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned logs by filtering
        against query parameters in the URL.
        """
        queryset = super().get_queryset()
        
        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
            
        # Filter by change type
        change_type = self.request.query_params.get('change_type')
        if change_type:
            queryset = queryset.filter(change_type=change_type)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        # Filter by path contains
        path_contains = self.request.query_params.get('path_contains')
        if path_contains:
            queryset = queryset.filter(file_path__icontains=path_contains)
            
        return queryset

# Move this function to module level, not inside a class
@never_cache  # Prevent caching to ensure latest changes are always visible
def file_change_logs(request):
    """Optimized view for file change logs with real-time updates and newest first sorting"""
    
    # Get filter parameters
    risk_level = request.GET.get('risk', None)
    days = request.GET.get('days', 7)
    search = request.GET.get('search', '')
    
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 7
    
    # Base queryset with optimization
    queryset = FileChangeLog.objects.select_related('analysis')
    
    # Apply filters
    if risk_level and risk_level != 'all':
        queryset = queryset.filter(risk_level=risk_level)
    
    if days > 0:
        cutoff_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=cutoff_date)
    
    if search:
        queryset = queryset.filter(
            Q(file_path__icontains=search) | 
            Q(change_type__icontains=search)
        )
    
    # Order by timestamp, most recent first - ensure this is applied
    queryset = queryset.order_by('-timestamp')
    
    # Only fetch necessary fields
    queryset = queryset.only(
        'timestamp', 'file_path', 'change_type', 
        'risk_level', 'recommendation'
    )
    
    # Paginate results - only load 50 at a time for faster loading
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_risk': risk_level or 'all',
        'filter_days': days,
        'search': search,
        'total_count': paginator.count,
        'current_time': timezone.now(),  # Add current time for auto-refresh
    }
    
    return render(request, 'file_management/file_change_logs.html', context)

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Re-analyze an existing file log"""
        file_log = self.get_object()
        
        try:
            # Check if file still exists
            if not os.path.exists(file_log.file_path):
                return Response({
                    'error': f"File not found: {file_log.file_path}",
                    'status': 'failed'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Read file content
            with open(file_log.file_path, 'rb') as f:
                content = f.read()
            
            # Set up metadata
            metadata = {
                'change_type': file_log.change_type,
                'timestamp': file_log.timestamp.isoformat(),
                'analyzed_by': request.user.username if request.user.is_authenticated else 'API request'
            }
            
            # Import SecurityAnalyzer here to avoid circular imports
            from .file_monitor.ai_analyzer.simple_analyzer import SecurityAnalyzer
            
            # Perform security analysis
            analyzer = SecurityAnalyzer()
            result = analyzer.analyze_file(
                file_path=file_log.file_path,
                file_content=content,
                metadata=metadata
            )
            
            # Update the FileChangeLog with analysis results
            file_log.risk_level = result['risk_analysis']['risk_level']
            file_log.recommendation = result['recommendation']
            
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
            
            # Link analysis to log entry
            file_log.analysis = analysis
            file_log.save()
            
            # Return the analysis result
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_log.file_path}: {e}")
            return Response({
                'error': str(e),
                'status': 'failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Find your chatgpt_prompt method and update it to include detailed findings

@action(detail=True, methods=['get'])
def chatgpt_prompt(self, request, pk=None):
    """Generate a ChatGPT prompt for security guidance"""
    file_log = self.get_object()
    
    try:
        # Get file name
        file_name = os.path.basename(file_log.file_path)
        
        # Build a detailed prompt
        prompt = f"Current Date and Time (UTC): {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        prompt += f"Current User's Login: {os.environ.get('USERNAME', 'user')}\n\n"
        prompt += f"SECURITY ALERT DETAILS\n"
        prompt += f"=====================\n\n"
        prompt += f"Risk Level: {file_log.risk_level.upper() if file_log.risk_level else 'UNKNOWN'}\n"
        prompt += f"Event Type: {file_log.change_type.upper() if file_log.change_type else 'UNKNOWN'}\n"
        prompt += f"File Name: {file_name}\n"
        prompt += f"File Path: {file_log.file_path}\n"
        prompt += f"Timestamp: {file_log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Include the recommendation
        if file_log.recommendation:
            prompt += f"Security Analysis:\n{file_log.recommendation}\n\n"
        
        # Include analysis details if available
        if file_log.analysis and file_log.analysis.analysis_result:
            # Format the detailed findings more prominently
            findings = file_log.analysis.analysis_result.get('risk_analysis', {}).get('detailed_findings', [])
            if findings:
                prompt += "DETAILED SECURITY FINDINGS:\n"
                prompt += "==========================\n"
                for i, finding in enumerate(findings, 1):
                    severity = finding.get('severity', finding.get('risk_level', 'Unknown')).upper()
                    prompt += f"{i}. [{severity}] {finding.get('description', 'Unknown finding')}\n"
                    if 'recommendation' in finding:
                        prompt += f"   Recommendation: {finding['recommendation']}\n"
                prompt += "\n"
            
            # Add technical details if available
            tech_details = file_log.analysis.analysis_result.get('file_info', {})
            if tech_details:
                prompt += "Technical File Information:\n"
                prompt += f"- File type: {tech_details.get('file_type', 'Unknown')}\n"
                prompt += f"- File size: {tech_details.get('size_bytes', 'Unknown')} bytes\n"
                prompt += f"- Hash: {tech_details.get('hash', 'Unknown')}\n\n"
        
        # Include what to ask ChatGPT
        prompt += f"Based on this security alert, please provide:\n"
        prompt += f"1. An assessment of the potential risk and impact\n"
        prompt += f"2. Recommended immediate actions to address this issue\n"
        prompt += f"3. Long-term preventive measures to avoid similar security concerns"
        
        return Response({
            'prompt': prompt
        })
        
    except Exception as e:
        logger.error(f"Error generating ChatGPT prompt: {e}")
        return Response({
            'error': str(e),
            'status': 'failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_monitored_directories(request):
    """Return the currently monitored directories from the config file."""
    config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Create a list of directory objects with name and path
            directories = []
            for path in config.get('paths', []):
                name = os.path.basename(path.rstrip('/\\'))
                directories.append({
                    'id': len(directories) + 1,
                    'name': name,
                    'path': path
                })
                
            return Response({
                'directories': directories,
                'last_updated': config.get('last_updated', '2025-08-04 07:45:54')
            })
        else:
            return Response({
                'directories': [],
                'last_updated': '2025-08-04 07:45:54'
            })
            
    except Exception as e:
        logger.error(f"Error getting monitored directories: {e}")
        return Response({
            'error': str(e),
            'directories': [],
            'last_updated': '2025-08-04 07:45:54'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_statistics(request):
    """Provide statistics about monitored files and events"""
    try:
        # Use aggregation for efficient counting
        from django.db.models import Count, Case, When, IntegerField
        
        # Get counts with a single database query
        risk_counts = FileChangeLog.objects.aggregate(
            total=Count('id'),
            safe=Count(Case(When(risk_level='safe', then=1), output_field=IntegerField())),
            suspicious=Count(Case(When(risk_level='suspicious', then=1), output_field=IntegerField())),
            dangerous=Count(Case(When(risk_level='dangerous', then=1), output_field=IntegerField())),
            unknown=Count(Case(When(risk_level='unknown', then=1), output_field=IntegerField())),
        )
        
        # Get most recent logs - limited to just 5
        recent_logs = FileChangeLog.objects.order_by('-timestamp')[:5]
        recent_data = []
        
        for log in recent_logs:
            recent_data.append({
                'id': log.id,
                'file_path': log.file_path,
                'file_name': os.path.basename(log.file_path),
                'change_type': log.change_type,
                'risk_level': log.risk_level,
                'timestamp': log.timestamp
            })
        
        return Response({
            'total_logs': risk_counts['total'],
            'risk_breakdown': {
                'safe': risk_counts['safe'],
                'suspicious': risk_counts['suspicious'], 
                'dangerous': risk_counts['dangerous'],
                'unknown': risk_counts['unknown']
            },
            'recent_logs': recent_data,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        logger.error(f"Error generating statistics: {e}")
        return Response({
            'error': str(e),
            'status': 'failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_config_file_path():
    """Get the path to the monitor_config.json file"""
    return os.path.join(settings.BASE_DIR, 'monitor_config.json')

@csrf_protect
def monitor_status(request):
    """Get the current status of the file monitor"""
    monitor = get_monitor_thread()
    is_running = monitor is not None and monitor.is_alive()
    
    monitored_paths = []
    if is_running and hasattr(monitor, 'paths'):
        for path in monitor.paths:
            monitored_paths.append({
                'path': path,
                'exists': os.path.exists(path)
            })
    
    # Get config
    config_file = get_config_file_path()
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            pass
    
    return JsonResponse({
        'status': 'running' if is_running else 'stopped',
        'monitored_paths': monitored_paths,
        'config': config,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    })

@csrf_protect
def start_monitor(request):
    """Start the file monitor"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})
        
    monitor = get_monitor_thread()
    if monitor and monitor.is_alive():
        return JsonResponse({
            'success': False,
            'message': 'Monitor is already running'
        })
    
    try:
        monitor = ensure_single_monitor()
        if monitor and monitor.is_alive():
            return JsonResponse({
                'success': True,
                'message': 'Monitor started successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to start monitor'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error starting monitor: {str(e)}'
        })

@csrf_protect
def stop_monitor_view(request):
    """Stop the file monitor"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})
        
    if stop_monitor():
        return JsonResponse({
            'success': True,
            'message': 'Monitor stopped successfully'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'No monitor was running'
        })

@csrf_protect
def restart_monitor(request):
    """Restart the file monitor"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})
        
    stop_monitor()
    try:
        monitor = ensure_single_monitor()
        if monitor and monitor.is_alive():
            return JsonResponse({
                'success': True,
                'message': 'Monitor restarted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to restart monitor'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error restarting monitor: {str(e)}'
        })

@csrf_protect
def update_directories(request):
    """Update the monitored directories"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})
    
    try:
        data = json.loads(request.body)
        directories = data.get('directories', [])
        
        if not directories:
            return JsonResponse({
                'success': False,
                'message': 'No directories provided'
            })
        
        # Validate directories
        valid_directories = []
        invalid_directories = []
        for directory in directories:
            if os.path.exists(directory) and os.path.isdir(directory):
                valid_directories.append(directory)
            else:
                invalid_directories.append(directory)
        
        if not valid_directories:
            return JsonResponse({
                'success': False,
                'message': 'No valid directories provided'
            })
        
        # Update config
        config_file = get_config_file_path()
        config = {}
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        config['paths'] = valid_directories
        config['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Restart monitor if it was running
        was_running = get_monitor_thread() is not None and get_monitor_thread().is_alive()
        if was_running:
            stop_monitor()
            ensure_single_monitor()
        
        message = 'Directories updated successfully'
        if invalid_directories:
            message += f". Warning: {len(invalid_directories)} invalid directories were skipped."
        
        return JsonResponse({
            'success': True,
            'message': message,
            'directories': valid_directories,
            'invalid_directories': invalid_directories,
            'monitor_restarted': was_running
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating directories: {str(e)}'
        })

@csrf_protect
def run_scan(request):
    """Run an immediate scan"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})
        
    monitor = get_monitor_thread()
    if not monitor or not monitor.is_alive():
        return JsonResponse({
            'success': False,
            'message': 'Monitor is not running'
        })
    
    try:
        if hasattr(monitor, 'run_full_scan'):
            monitor.run_full_scan()
            return JsonResponse({
                'success': True,
                'message': 'Scan started successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Monitor does not support full scan'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error starting scan: {str(e)}'
        })

@csrf_protect
def set_scan_interval(request):
    """Set the scan interval in minutes"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'})
        
    try:
        data = json.loads(request.body)
        minutes = data.get('minutes', None)
        
        if minutes is None:
            return JsonResponse({
                'success': False,
                'message': 'Minutes parameter is required'
            })
            
        try:
            minutes = int(minutes)
            if minutes < 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Interval must be at least 1 minute'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Interval must be a valid number'
            })
        
        # Update config
        config_file = get_config_file_path()
        config = {}
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        config['full_scan_interval_minutes'] = minutes
        config['last_updated'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return JsonResponse({
            'success': True,
            'message': f'Scan interval updated to {minutes} minutes',
            'minutes': minutes
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error setting scan interval: {str(e)}'
        })