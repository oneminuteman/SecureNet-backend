import logging
from datetime import timedelta
from django.utils import timezone
from django.db import connection, transaction
import os
import json
from django.conf import settings

logger = logging.getLogger(__name__)

# Singleton instance
_cleanup_manager = None

def get_cleanup_manager():
    """Get the singleton cleanup manager instance"""
    global _cleanup_manager
    if _cleanup_manager is None:
        _cleanup_manager = LogCleanupManager()
    return _cleanup_manager

class LogCleanupManager:
    """Manages automatic log cleanup based on retention policy"""
    
    def __init__(self):
        """Initialize with configuration"""
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from config file"""
        default_config = {
            'auto_cleanup_enabled': True,
            'days_to_keep': 3,
            'max_records': 1000,
            'cleanup_interval_hours': 12
        }
        
        # Try to load from file
        config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # Extract log retention settings
                if 'log_retention' in config:
                    retention_config = config['log_retention']
                    # Update defaults with file values
                    for key in default_config:
                        if key in retention_config:
                            default_config[key] = retention_config[key]
            except Exception as e:
                logger.error(f"Error loading cleanup config: {e}")
                
        return default_config
        
    def perform_cleanup(self):
        """Perform log cleanup based on configured retention policy"""
        if not self.config.get('auto_cleanup_enabled', True):
            logger.info("Automatic log cleanup is disabled")
            return {'success': True, 'message': 'Automatic cleanup is disabled'}
            
        logger.info("Starting automatic log cleanup")
        
        try:
            from myapp.models import FileChangeLog, FileAnalysis
            import time
            
            start_time = time.time()
            
            # Get configuration values
            days_to_keep = self.config.get('days_to_keep', 3)
            max_records = self.config.get('max_records', 1000)
            
            with transaction.atomic():
                # 1. Delete logs older than retention period
                cutoff_date = timezone.now() - timedelta(days=days_to_keep)
                old_logs_deleted = FileChangeLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
                logger.info(f"Deleted {old_logs_deleted} logs older than {days_to_keep} days")
                
                # 2. Determine timestamp field for FileAnalysis (created_at or timestamp)
                timestamp_field = 'created_at'
                if not hasattr(FileAnalysis, 'created_at'):
                    timestamp_field = 'timestamp'
                
                # 3. Delete old analysis records
                filter_kwargs = {f"{timestamp_field}__lt": cutoff_date}
                old_analysis_deleted = FileAnalysis.objects.filter(**filter_kwargs).delete()[0]
                logger.info(f"Deleted {old_analysis_deleted} analysis records older than {days_to_keep} days")
                
                # 4. Limit total log records
                total_logs = FileChangeLog.objects.count()
                excess_logs_deleted = 0
                
                if total_logs > max_records:
                    # Get cutoff point - the timestamp of the oldest record to keep
                    cutoff_logs = FileChangeLog.objects.order_by('-timestamp')[max_records-1:max_records]
                    if cutoff_logs:
                        cutoff_time = cutoff_logs[0].timestamp
                        excess_logs_deleted = FileChangeLog.objects.filter(timestamp__lt=cutoff_time).delete()[0]
                        logger.info(f"Deleted {excess_logs_deleted} excess logs to maintain {max_records} limit")
                
                # 5. Limit total analysis records
                total_analysis = FileAnalysis.objects.count()
                excess_analysis_deleted = 0
                
                if total_analysis > max_records:
                    # Get cutoff point - the timestamp of the oldest record to keep
                    order_by = f"-{timestamp_field}"
                    cutoff_analysis = FileAnalysis.objects.order_by(order_by)[max_records-1:max_records]
                    if cutoff_analysis:
                        cutoff_time = getattr(cutoff_analysis[0], timestamp_field)
                        filter_kwargs = {f"{timestamp_field}__lt": cutoff_time}
                        excess_analysis_deleted = FileAnalysis.objects.filter(**filter_kwargs).delete()[0]
                        logger.info(f"Deleted {excess_analysis_deleted} excess analysis records to maintain {max_records} limit")
            
            # Outside transaction - optimize database
            cursor = connection.cursor()
            cursor.execute('VACUUM;')
            logger.info("Database optimized with VACUUM")
            
            # Get current counts
            current_logs = FileChangeLog.objects.count()
            current_analysis = FileAnalysis.objects.count()
            
            duration = time.time() - start_time
            
            return {
                'success': True,
                'old_logs_deleted': old_logs_deleted,
                'old_analysis_deleted': old_analysis_deleted,
                'excess_logs_deleted': excess_logs_deleted,
                'excess_analysis_deleted': excess_analysis_deleted,
                'current_logs': current_logs,
                'current_analysis': current_analysis,
                'duration_seconds': duration
            }
                
        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def emergency_cleanup(self):
        """Perform an emergency cleanup to drastically reduce log volume"""
        from django.db import connection
        from django.utils import timezone
        from myapp.models import FileChangeLog, FileAnalysis
        import datetime
        
        try:
            # Get current counts
            log_count = FileChangeLog.objects.count()
            analysis_count = FileAnalysis.objects.count()
            
            logger.info(f"Emergency cleanup starting - Current counts: {log_count} logs, {analysis_count} analysis records")
            
            # Keep only last 24 hours plus 500 most recent records
            cutoff_date = timezone.now() - datetime.timedelta(days=1)
            
            # First delete older records
            deleted_logs = FileChangeLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
            
            # Find out if field is timestamp or created_at for FileAnalysis
            timestamp_field = 'created_at' if hasattr(FileAnalysis, 'created_at') else 'timestamp'
            
            # Use correct field name for deletion
            if timestamp_field == 'created_at':
                deleted_analysis = FileAnalysis.objects.filter(created_at__lt=cutoff_date).delete()[0]
            else:
                deleted_analysis = FileAnalysis.objects.filter(timestamp__lt=cutoff_date).delete()[0]
            
            # Now limit to 500 records if still more
            if FileChangeLog.objects.count() > 500:
                cutoff_log = FileChangeLog.objects.order_by('-timestamp')[499:500].first()
                if cutoff_log:
                    excess_deleted = FileChangeLog.objects.filter(timestamp__lt=cutoff_log.timestamp).delete()[0]
                    logger.info(f"Deleted {excess_deleted} excess logs")
            
            # Same for analysis
            if FileAnalysis.objects.count() > 500:
                if timestamp_field == 'created_at':
                    cutoff_analysis = FileAnalysis.objects.order_by('-created_at')[499:500].first()
                    if cutoff_analysis:
                        excess_deleted = FileAnalysis.objects.filter(created_at__lt=cutoff_analysis.created_at).delete()[0]
                        logger.info(f"Deleted {excess_deleted} excess analysis records")
                else:
                    cutoff_analysis = FileAnalysis.objects.order_by('-timestamp')[499:500].first()
                    if cutoff_analysis:
                        excess_deleted = FileAnalysis.objects.filter(timestamp__lt=cutoff_analysis.timestamp).delete()[0]
                        logger.info(f"Deleted {excess_deleted} excess analysis records")
            
            # Optimize database
            cursor = connection.cursor()
            cursor.execute('VACUUM;')
            
            # Get new counts
            new_log_count = FileChangeLog.objects.count()
            new_analysis_count = FileAnalysis.objects.count()
            
            logger.info(f"Emergency cleanup completed - New counts: {new_log_count} logs, {new_analysis_count} analysis records")
            logger.info(f"Reduced by: {log_count - new_log_count} logs, {analysis_count - new_analysis_count} analysis records")
            
            return {
                'success': True,
                'logs_removed': log_count - new_log_count,
                'analysis_removed': analysis_count - new_analysis_count,
                'current_logs': new_log_count,
                'current_analysis': new_analysis_count
            }
        
        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")
            return {
                'success': False,
                'error': str(e)
            }