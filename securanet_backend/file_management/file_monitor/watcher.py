import os
import time
import logging
import threading
import queue
import json
from datetime import datetime
from pathlib import Path
from django.utils import timezone
from django.conf import settings

from ..models import FileChangeLog, FileAnalysis
from .ai_analyzer.simple_analyzer import SecurityAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileMonitorThread(threading.Thread):
    """Main thread that monitors multiple directories"""
    
    def __init__(self, paths=None):
        threading.Thread.__init__(self, daemon=True)
        self.name = "SecureNet-FileMonitor"
        self.stop_event = threading.Event()
        self.file_queue = queue.Queue()
        self.monitored_directories = {}
        
        # Load configuration
        self.config = self.load_config()
        
        # Set up paths to monitor
        self.paths = paths or []
        if not self.paths and 'paths' in self.config:
            self.paths = self.config.get('paths', [])
            
        # Initialize security analyzer
        self.analyzer = SecurityAnalyzer()
        
        # Logging setup
        logger.info(f"Initializing file monitor with paths: {self.paths}")
        
    def load_config(self):
        """Load monitoring configuration"""
        config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_file}")
                return config
            except Exception as e:
                logger.error(f"Error reading config: {e}")
                
        # Default configuration
        logger.warning("Using default configuration")
        return {
            'mode': 'custom',
            'paths': [os.path.expanduser('~/Documents')]
        }
    
    def run(self):
        """Main monitoring thread function"""
        logger.info("Starting file monitor thread...")
        
        # Create file cache directory
        Path('./file_state_cache').mkdir(exist_ok=True)
        
        # Start monitoring each directory
        for path in self.paths:
            if os.path.exists(path):
                watcher = DirectoryWatcher(path, self.file_queue, self.stop_event)
                watcher.start()
                self.monitored_directories[path] = watcher
                logger.info(f"Started monitoring directory: {path}")
            else:
                logger.warning(f"Directory not found, skipping: {path}")
        
        # If no valid paths were found, monitor Documents as fallback
        if not self.monitored_directories:
            fallback = os.path.expanduser('~/Documents')
            watcher = DirectoryWatcher(fallback, self.file_queue, self.stop_event)
            watcher.start()
            self.monitored_directories[fallback] = watcher
            logger.info(f"No valid paths found, using fallback: {fallback}")
        
        # Process files from the queue
        while not self.stop_event.is_set():
            try:
                # Get file from queue with timeout
                try:
                    event_type, path = self.file_queue.get(timeout=1)
                    self.process_file(event_type, path)
                except queue.Empty:
                    continue
            except Exception as e:
                logger.error(f"Error in monitor thread: {e}")
                time.sleep(1)  # Avoid tight loop on repeated errors
        
        # Stop all directory watchers
        for path, watcher in self.monitored_directories.items():
            watcher.stop()
            logger.info(f"Stopped monitoring directory: {path}")
            
        logger.info("File monitor thread stopped")

    def run_full_scan(self):
        # "Run a full scan of all monitored directories"
        logger.info("Starting full system scan...")
        
        # Force each directory watcher to rescan
        for path, watcher in self.monitored_directories.items():
            logger.info(f"Running full scan on: {path}")
            # Reset file states to force detection of all files
            watcher.file_states = {}
            # Run a scan cycle
            watcher.scan_directory(initial=False)
        
        logger.info("Full system scan completed")
        return True
    
    def process_file(self, event_type_or_path, path=None):
        # Handle the case when only a path is provided
        if path is None:
            path = event_type_or_path
            event_type = 'scanned'  # Default event type for single-argument calls
        else:
            event_type = event_type_or_path
        
        logger.info(f"Processing {event_type} event for: {path}")
        
        # Skip directories
        if os.path.isdir(path):
            return
        
        # Handle deleted files
        if event_type == 'deleted' or not os.path.exists(path):
            FileChangeLog.objects.create(
                file_path=path,
                change_type=event_type,
                risk_level='unknown',
                recommendation='File was deleted or is no longer accessible',
                timestamp=timezone.now()
            )
            logger.info(f"Logged deleted file: {path}")
            return
        
        # For existing files
        try:
            # Create initial log entry
            log_entry = FileChangeLog.objects.create(
                file_path=path,
                change_type=event_type,
                risk_level='unknown',
                timestamp=timezone.now()
            )
            
            # Check file size - skip very large files
            file_size = os.path.getsize(path)
            max_size = 10 * 1024 * 1024  # 10MB
            
            if file_size > max_size:
                log_entry.recommendation = f"File too large for analysis ({file_size} bytes)"
                log_entry.save()
                logger.info(f"Skipping large file: {path}")
                return
            
            # Read file content
            with open(path, 'rb') as f:
                content = f.read()
            
            # Set up metadata
            metadata = {
                'change_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'analyzed_by': 'SecureNet Monitor'
            }
            
            # Perform security analysis
            result = self.analyzer.analyze_file(
                file_path=path,
                file_content=content,
                metadata=metadata
            )
            
            # Extract filename for better display
            filename = os.path.basename(path)
            
            # Update log entry with analysis results
            log_entry.risk_level = result['risk_analysis']['risk_level']
            log_entry.recommendation = result['recommendation']
            
            # Create detailed analysis record
            analysis = FileAnalysis.objects.create(
                file_path=path,
                content_hash=result['file_info']['hash'],
                risk_score=result['risk_analysis']['overall_score'],
                risk_level=result['risk_analysis']['risk_level'],
                analysis_result=result,
                created_at=timezone.now()
            )
            
            # Link analysis to log entry
            log_entry.analysis = analysis
            log_entry.save()
            
            # Log based on risk level
            # Replace this section in your process_file method 
# (around line 150-170 where the risk level logging happens)

# Log based on risk level
            if result['risk_analysis']['risk_level'] == 'dangerous':
                # Extract the specific dangerous findings
                danger_reasons = []
                for finding in result['risk_analysis'].get('detailed_findings', []):
                    if finding.get('severity', '').lower() == 'high' or finding.get('risk_level', '').lower() == 'dangerous':
                        danger_reasons.append(finding.get('description', 'Unknown threat'))
                
                # Create a more informative message
                if danger_reasons:
                    danger_details = ", ".join(danger_reasons)
                    warning_message = f"🚨 DANGEROUS FILE DETECTED: {filename} - REASON: {danger_details}"
                else:
                    warning_message = f"🚨 DANGEROUS FILE DETECTED: {filename} - Overall risk assessment indicates danger"
                
                # Log the detailed warning
                logger.warning(warning_message)
                print(warning_message)
                
            elif result['risk_analysis']['risk_level'] == 'suspicious':
                logger.warning(f"⚠️ Suspicious file detected: {filename}")
                print(f"⚠️ Suspicious file detected: {filename}")
            else:
                logger.info(f"✅ File analyzed as safe: {filename}")
                
        except Exception as e:
            logger.error(f"Error analyzing file {path}: {e}")
            FileChangeLog.objects.create(
                file_path=path,
                change_type=event_type,
                risk_level='unknown',
                recommendation=f'Error during analysis: {str(e)}',
                timestamp=timezone.now()
            )
    
    def stop(self):
        """Stop the monitoring thread"""
        logger.info("Stopping file monitor thread...")
        self.stop_event.set()


class DirectoryWatcher(threading.Thread):
    """Watches a single directory for changes"""
    
    def __init__(self, directory, file_queue, stop_event):
        threading.Thread.__init__(self, daemon=True)
        self.directory = directory
        self.file_queue = file_queue
        self.stop_event = stop_event
        self.file_states = {}  # Path -> (mtime, size)
        self.interval = 1.0  # 1 second scan interval for faster response
    
    def run(self):
        """Main directory watching loop"""
        logger.info(f"Starting directory watcher for: {self.directory}")
        
        # Initial scan to build state
        self.scan_directory(initial=True)
        
        # Main monitoring loop
        while not self.stop_event.is_set():
            try:
                self.scan_directory(initial=False)
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error scanning directory {self.directory}: {e}")
                time.sleep(5)  # Longer delay on error
    
    def scan_directory(self, initial=False):
        """Scan the directory for changes"""
        current_states = {}
        
        # Walk the directory recursively
        for root, dirs, files in os.walk(self.directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Process each file
            for file in files:
                # Skip hidden and temporary files
                if file.startswith('.') or file.endswith('.tmp'):
                    continue
                    
                full_path = os.path.join(root, file)
                
                try:
                    # Get file info
                    stat = os.stat(full_path)
                    mtime = stat.st_mtime
                    size = stat.st_size
                    
                    # Store current state
                    current_states[full_path] = (mtime, size)
                    
                    # Check for changes (if not initial scan)
                    if not initial and full_path in self.file_states:
                        old_mtime, old_size = self.file_states[full_path]
                        
                        if mtime > old_mtime or size != old_size:
                            # File was modified
                            self.file_queue.put(('modified', full_path))
                    elif not initial:
                        # New file
                        self.file_queue.put(('created', full_path))
                except (FileNotFoundError, PermissionError):
                    # Skip files we can't access
                    pass
                except Exception as e:
                    logger.error(f"Error processing file {full_path}: {e}")
        
        # Check for deleted files
        if not initial:
            for path in self.file_states:
                if path not in current_states:
                    self.file_queue.put(('deleted', path))
        
        # Update file states
        self.file_states = current_states
    
    def stop(self):
        """Nothing to do here as we use the shared stop_event"""
        pass


# Global monitor thread reference
_monitor_thread = None
_monitor_lock = threading.Lock()

def get_monitor_thread():
    """Get the current monitor thread if it exists"""
    global _monitor_thread
    return _monitor_thread

def ensure_single_monitor(paths=None):
    """Ensure only one monitor thread is running"""
    global _monitor_thread, _monitor_lock
    
    with _monitor_lock:
        # If thread exists and is alive, return it
        if _monitor_thread is not None and _monitor_thread.is_alive():
            logger.info("Monitor thread already running")
            return _monitor_thread
            
        # Otherwise create a new thread
        _monitor_thread = FileMonitorThread(paths)
        _monitor_thread.start()
        logger.info("Started new monitor thread")
        
    return _monitor_thread

def stop_monitor():
    """Stop the running monitor thread"""
    global _monitor_thread
    
    if _monitor_thread is not None and _monitor_thread.is_alive():
        _monitor_thread.stop()
        _monitor_thread.join(timeout=5)
        _monitor_thread = None
        return True
    return False