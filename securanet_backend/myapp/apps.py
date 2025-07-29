from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Only start file monitor if not in migration or other management commands
        import sys
        
        # Prevent running twice in development
        if os.environ.get('RUN_MAIN') != 'true':
            return

        # Don't start monitor during migrations, tests, or other management commands
        if any(arg in sys.argv for arg in ['migrate', 'makemigrations', 'test', 'collectstatic']):
            logger.info("Skipping file monitor startup during management command")
            return
        
        try:
            from myapp.file_monitor.watcher import ensure_single_monitor
            ensure_single_monitor()
            logger.info("File monitor started successfully")
        except ImportError as e:
            logger.warning(f"File monitor module not found: {e}")
        except Exception as e:
            logger.error(f"Failed to start file monitor: {e}")
            # Don't let the app fail to start if monitor fails
            pass