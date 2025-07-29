import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.utils import timezone
from ..models import FileChangeLog, FileAnalysis
from .ai_analyzer.analyzer import SecurityAnalyzer
import hashlib
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.analyzer = SecurityAnalyzer()
        self.last_events = {}  # For deduplication
        super().__init__()

    def on_any_event(self, event):
        if event.is_directory:
            return

        # Deduplicate events
        current_time = time.time()
        if event.src_path in self.last_events:
            if current_time - self.last_events[event.src_path] < 1:  # 1 second window
                return
        self.last_events[event.src_path] = current_time

        try:
            if event.event_type in ['created', 'modified', 'deleted']:
                logger.info(f"📝 File {event.event_type}: {event.src_path}")
                
                # Create log entry
                log_entry = FileChangeLog.objects.create(
                    file_path=event.src_path,
                    change_type=event.event_type,
                    timestamp=timezone.now()
                )

                # Analyze file if it exists
                if event.event_type in ['created', 'modified'] and os.path.exists(event.src_path):
                    try:
                        with open(event.src_path, 'rb') as f:
                            content = f.read()
                            analysis_result = self.analyzer.analyze_file(event.src_path, content)
                            
                            # Update log entry with analysis
                            log_entry.risk_level = analysis_result['risk_analysis']['risk_level']
                            log_entry.recommendation = analysis_result['recommendation']
                            log_entry.save()
                            
                            logger.info(f"✅ Analysis completed for {event.src_path}")
                            logger.info(f"Risk Level: {log_entry.risk_level}")
                    except Exception as e:
                        logger.error(f"❌ Analysis failed for {event.src_path}: {str(e)}")
                        log_entry.risk_level = 'unknown'
                        log_entry.recommendation = f"Analysis failed: {str(e)}. Manual review recommended."
                        log_entry.save()

        except Exception as e:
            logger.error(f"❌ Error handling {event.event_type} event for {event.src_path}: {str(e)}")

class SimpleFileMonitor:
    """A simplified file monitor that uses basic polling instead of watchdog for Python 3.13+ compatibility"""
    def __init__(self, path_to_watch):
        self.path_to_watch = path_to_watch
        self.event_handler = FileEventHandler()
        self._stop_event = threading.Event()
        self._file_states = {}  # Stores last modified times

    def _scan_directory(self):
        """Scans the directory and detects changes"""
        current_files = {}
        
        try:
            # Get all files in the directory
            for filename in os.listdir(self.path_to_watch):
                filepath = os.path.join(self.path_to_watch, filename)
                if os.path.isfile(filepath):
                    current_files[filepath] = os.path.getmtime(filepath)
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            return
            
        # Check for new or modified files
        for filepath, mtime in current_files.items():
            if filepath not in self._file_states:
                # New file
                event = type('Event', (), {'event_type': 'created', 'src_path': filepath, 'is_directory': False})
                self.event_handler.on_any_event(event)
            elif self._file_states[filepath] != mtime:
                # Modified file
                event = type('Event', (), {'event_type': 'modified', 'src_path': filepath, 'is_directory': False})
                self.event_handler.on_any_event(event)
                
        # Check for deleted files
        for filepath in list(self._file_states.keys()):
            if filepath not in current_files:
                event = type('Event', (), {'event_type': 'deleted', 'src_path': filepath, 'is_directory': False})
                self.event_handler.on_any_event(event)
                
        # Update file states
        self._file_states = current_files

    def start(self):
        if not os.path.exists(self.path_to_watch):
            os.makedirs(self.path_to_watch, exist_ok=True)
            
        # Initial scan
        self._scan_directory()
        
        logger.info(f"🔍 Started simple polling monitor on: {self.path_to_watch}")
        print(f"🔍 File monitor started on: {self.path_to_watch}")  # Console output

        try:
            while not self._stop_event.is_set():
                self._scan_directory()
                time.sleep(2)  # Poll every 2 seconds
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"❌ Monitor error: {str(e)}")
            self.stop()
            raise
        
    def stop(self):
        self._stop_event.set()
        logger.info("📥 Stopped monitoring")
        print("📥 File monitor stopped")  # Console output

class FileMonitor:
    def __init__(self, path_to_watch):
        self.path_to_watch = path_to_watch
        self.event_handler = FileEventHandler()
        self.observer = Observer()
        self._stop_event = threading.Event()

    def start(self):
        if not os.path.exists(self.path_to_watch):
            os.makedirs(self.path_to_watch, exist_ok=True)
            
        self.observer.schedule(self.event_handler, self.path_to_watch, recursive=False)
        
        # Try to start observer in a way that works with Python 3.13
        try:
            if sys.version_info >= (3, 13):
                # For Python 3.13+, create a custom thread to run the observer
                self._thread = threading.Thread(
                    target=self._run_observer,
                    daemon=True
                )
                self._thread.start()
            else:
                # For older Python versions, use the normal method
                self.observer.start()
        except Exception as e:
            logger.error(f"Failed to start observer: {e}")
            logger.info("Falling back to simple file monitor")
            # Fall back to SimpleFileMonitor
            self.simple_monitor = SimpleFileMonitor(self.path_to_watch)
            self.simple_monitor.start()
            return
            
        logger.info(f"🔍 Started monitoring: {self.path_to_watch}")
        print(f"🔍 File monitor started on: {self.path_to_watch}")  # Console output

        try:
            while not self._stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"❌ Monitor error: {str(e)}")
            self.stop()
            raise
    
    def _run_observer(self):
        """Custom method to run the observer"""
        try:
            self.observer._started = True
            self.observer._run()
        except Exception as e:
            logger.error(f"Observer thread error: {e}")
        
    def stop(self):
        self._stop_event.set()
        if hasattr(self, 'simple_monitor'):
            self.simple_monitor.stop()
        else:
            if hasattr(self, '_thread') and self._thread.is_alive():
                self._thread.join(timeout=3)
            try:
                self.observer.stop()
                self.observer.join(timeout=3)
            except Exception as e:
                logger.error(f"Error stopping observer: {e}")
                
        logger.info("📥 Stopped monitoring")
        print("📥 File monitor stopped")  # Console output

def start_monitor_in_thread(path_to_watch=None):
    """
    Starts the file monitor in a separate thread.
    """
    from django.conf import settings
    
    if path_to_watch is None:
        path_to_watch = settings.WATCH_FOLDER

    def run_monitor():
        # For Python 3.13, use SimpleFileMonitor directly
        if sys.version_info >= (3, 13):
            logger.info("Using SimpleFileMonitor for Python 3.13+ compatibility")
            monitor = SimpleFileMonitor(path_to_watch)
        else:
            # Try FileMonitor first, it will fall back to SimpleFileMonitor if needed
            monitor = FileMonitor(path_to_watch)
            
        try:
            monitor.start()
        except Exception as e:
            logger.error(f"Monitor failed: {str(e)}")
            print(f"❌ Monitor failed: {str(e)}")  # Console output
        finally:
            monitor.stop()

    # Create thread with fixed name for easier debugging
    monitor_thread = threading.Thread(
        target=run_monitor, 
        daemon=True,
        name="SecureNet-FileMonitor"
    )
    monitor_thread.start()
    
    return monitor_thread

# Global monitor thread reference
_monitor_thread = None

def get_monitor_thread():
    """Get the current monitor thread if it exists."""
    global _monitor_thread
    return _monitor_thread

def ensure_single_monitor(path_to_watch=None):
    """
    Ensures only one monitor thread is running.
    Starts a new one if none exists.
    """
    global _monitor_thread
    
    if _monitor_thread and _monitor_thread.is_alive():
        logger.info("Monitor thread already running")
        return _monitor_thread
        
    _monitor_thread = start_monitor_in_thread(path_to_watch)
    return _monitor_thread