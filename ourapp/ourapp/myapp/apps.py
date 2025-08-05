from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Import here to avoid circular imports
        from django.conf import settings
        
        # Skip in management commands
        import sys
        if 'manage.py' in sys.argv and ('runserver' not in sys.argv and 'runmonitor' not in sys.argv):
            return
            
        # Start log cleanup scheduler
        self.start_log_cleanup_scheduler()
        
        # Other startup code...
    
    def start_log_cleanup_scheduler(self):
        """Start a background thread for scheduled log cleanup"""
        def cleanup_worker():
            from myapp.log_management.auto_cleanup import get_cleanup_manager
            
            # Wait a bit before first cleanup
            time.sleep(60)
            
            while True:
                try:
                    cleanup_manager = get_cleanup_manager()
                    if cleanup_manager.config.get('auto_cleanup_enabled', True):
                        logger.info("Running scheduled log cleanup")
                        result = cleanup_manager.perform_cleanup()
                        if result.get('success', False):
                            logger.info(f"Log cleanup successful, current count: {result.get('current_logs', 'unknown')}")
                        else:
                            logger.error(f"Log cleanup failed: {result.get('error', 'unknown error')}")
                except Exception as e:
                    logger.error(f"Error in cleanup scheduler: {e}")
                
                # Sleep for the configured interval
                hours = 6  # Default
                try:
                    from django.conf import settings
                    import json
                    import os
                    
                    config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
                    if os.path.exists(config_file):
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                            hours = config.get('log_retention', {}).get('cleanup_interval_hours', 6)
                except Exception:
                    pass
                
                # Sleep for the specified hours
                time.sleep(hours * 60 * 60)
        
        # Start the cleanup thread
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()