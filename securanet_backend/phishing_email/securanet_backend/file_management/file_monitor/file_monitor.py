import os
import time
import logging
import threading
import hashlib
import json
import queue
from datetime import datetime
from pathlib import Path
from django.utils import timezone

logger = logging.getLogger(__name__)

class ReliableFileMonitor:
    """A reliable file monitoring system that works consistently across platforms"""
    
    def __init__(self, paths, event_callback, config):
        self.paths = paths
        self.event_callback = event_callback
        self.config = config
        self.stop_event = threading.Event()
        self.file_states = {}
        self.scan_interval = 1.0  # scan more frequently for better response
        self.thread = None
        
    def start(self):
        """Start the file monitoring thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("Monitor thread is already running")
            return self
            
        logger.info(f"Starting file monitor on paths: {self.paths}")
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return self
        
    def stop(self):
        """Stop the file monitoring thread"""
        logger.info("Stopping file monitor")
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        logger.info("File monitor stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info(f"File monitor started on paths: {', '.join(self.paths)}")
        
        # Initial scan to build state
        try:
            logger.info("Building initial file state cache...")
            self._scan_directories(initial=True)
            logger.info(f"Initial scan complete. Tracking {len(self.file_states)} files.")
        except Exception as e:
            logger.error(f"Error during initial scan: {e}")
        
        # Main monitoring loop
        scan_count = 0
        while not self.stop_event.is_set():
            try:
                # Scan for changes
                scan_count += 1
                changes = self._scan_directories(initial=False)
                
                # Every 60 scans, log the status
                if scan_count % 60 == 0:
                    logger.info(f"Monitor is running. Tracking {len(self.file_states)} files.")
                    scan_count = 0
                
                # Sleep for the scan interval
                time.sleep(self.scan_interval)
            except Exception as e:
                logger.error(f"Error in file monitoring loop: {e}")
                time.sleep(5)  # Avoid tight loop if there's an error
                
    def _scan_directories(self, initial=False):
        """Scan directories for changes"""
        current_states = {}
        changes_detected = 0
        
        # Ensure paths is a list
        if not isinstance(self.paths, list):
            logger.warning(f"Paths is not a list: {self.paths}")
            if isinstance(self.paths, str):
                paths_to_scan = [self.paths]
            else:
                paths_to_scan = []
        else:
            paths_to_scan = self.paths
            
        # Debug log when we're doing a full scan
        if not initial and len(paths_to_scan) > 0:
            logger.debug(f"Scanning {len(paths_to_scan)} directories for changes")
        
        for base_path in paths_to_scan:
            if not os.path.exists(base_path):
                if not initial:  # Only log this after the initial scan
                    logger.warning(f"Path does not exist: {base_path}")
                continue
                
            try:
                for root, dirs, files in os.walk(base_path):
                    # Check if we should stop
                    if self.stop_event.is_set():
                        return changes_detected
                        
                    # Skip excluded directories
                    dirs_to_remove = []
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        if self._should_ignore_file(dir_path):
                            dirs_to_remove.append(d)
                    
                    for d in dirs_to_remove:
                        if d in dirs:
                            dirs.remove(d)
                    
                    # Process each file
                    for file in files:
                        full_path = os.path.join(root, file)
                        
                        # Skip if should be ignored
                        if self._should_ignore_file(full_path):
                            continue
                            
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
                                    logger.info(f"📝 Modified: {full_path}")
                                    self.event_callback('modified', full_path)
                                    changes_detected += 1
                            elif not initial:
                                # New file
                                logger.info(f"📝 Created: {full_path}")
                                self.event_callback('created', full_path)
                                changes_detected += 1
                        except (FileNotFoundError, PermissionError):
                            # Skip files we can't access
                            pass
                        except Exception as e:
                            logger.error(f"Error processing file {full_path}: {e}")
            except Exception as e:
                logger.error(f"Error scanning directory {base_path}: {e}")
        
        # Check for deleted files
        if not initial:
            for path in self.file_states:
                if path not in current_states:
                    try:
                        logger.info(f"📝 Deleted: {path}")
                        self.event_callback('deleted', path)
                        changes_detected += 1
                    except Exception as e:
                        logger.error(f"Error processing deleted file {path}: {e}")
        
        # Update states
        self.file_states = current_states
        return changes_detected
    
    def _should_ignore_file(self, path):
        """Check if a file should be ignored based on configuration"""
        # Skip directories if configured
        if os.path.isdir(path) and self.config.get('IGNORE_DIRECTORIES', True):
            return True
            
        # Skip temp files if configured
        if self.config.get('IGNORE_TEMP_FILES', True):
            if path.endswith('.tmp') or path.endswith('.temp') or '~$' in os.path.basename(path):
                return True
        
        # Check excluded paths from config
        exclusions = self.config.get('monitoring', {}).get('exclusions', {}).get('paths', [])
        for exclusion in exclusions:
            if self._path_matches_pattern(path, exclusion):
                return True
        
        # Check excluded extensions from config
        excluded_extensions = self.config.get('monitoring', {}).get('exclusions', {}).get('extensions', [])
        ext = os.path.splitext(path)[1].lower()
        if ext in excluded_extensions:
            return True
            
        # Check file size limits
        try:
            max_size_mb = self.config.get('monitoring', {}).get('exclusions', {}).get('size_limits', {}).get('max_file_size_mb', 0)
            if max_size_mb > 0 and os.path.isfile(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                if size_mb > max_size_mb:
                    return True
        except:
            pass
            
        return False
    
    def _path_matches_pattern(self, path, pattern):
        """Check if a path matches a glob-like pattern"""
        import fnmatch
        
        # Convert Windows backslashes to forward slashes for consistent matching
        normalized_path = path.replace('\\', '/')
        
        return fnmatch.fnmatch(normalized_path, pattern)


class FileEventHandler:
    """Handles file events and manages file state cache"""
    
    def __init__(self, file_queue, config):
        self.file_queue = file_queue
        self.config = config
        self.file_cache = {}
        self.load_file_cache()
        self.last_seen = {}
        self.dedup_window = int(os.environ.get('DEDUP_WINDOW_SECONDS', 5))
        
    def load_file_cache(self):
        """Load file cache from disk if it exists"""
        cache_file = Path('./file_state_cache/file_state.json')
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.file_cache = json.load(f)
                logger.info(f"Loaded file cache with {len(self.file_cache)} entries")
            except Exception as e:
                logger.error(f"Error loading file cache: {e}")
                self.file_cache = {}
    
    def save_file_cache(self):
        """Save file cache to disk"""
        cache_file = Path('./file_state_cache/file_state.json')
        cache_file.parent.mkdir(exist_ok=True)
        try:
            # Only keep the most recent 10,000 entries to prevent unbounded growth
            if len(self.file_cache) > 10000:
                # Convert to list of tuples, sort by timestamp, and keep only the newest 10,000
                items = [(k, v) for k, v in self.file_cache.items()]
                items.sort(key=lambda x: x[1].get('timestamp', 0), reverse=True)
                self.file_cache = {k: v for k, v in items[:10000]}
            
            with open(cache_file, 'w') as f:
                json.dump(self.file_cache, f)
        except Exception as e:
            logger.error(f"Error saving file cache: {e}")
    
    def compute_file_hash(self, path):
        """Compute a fast hash of the file"""
        try:
            if not os.path.isfile(path):
                return None
                
            # Use xxhash if available, fallback to md5
            try:
                import xxhash
                hasher = xxhash.xxh64()
            except ImportError:
                hasher = hashlib.md5()
            
            # Get file stat info
            stat = os.stat(path)
            file_size = stat.st_size
            
            # For very large files, just hash the first and last 1MB
            # This is much faster and still catches most changes
            if file_size > 2 * 1024 * 1024:  # If larger than 2MB
                with open(path, 'rb') as f:
                    # Read first 1MB
                    hasher.update(f.read(1024 * 1024))
                    # Seek to last 1MB
                    f.seek(-1024 * 1024, 2)
                    # Read last 1MB
                    hasher.update(f.read(1024 * 1024))
            else:
                # For smaller files, read the entire content
                with open(path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        hasher.update(chunk)
            
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {path}: {e}")
            return None
    
    def has_file_changed(self, path):
        """Check if a file has actually changed based on content hash"""
        if not os.path.exists(path) or not os.path.isfile(path):
            # File doesn't exist or isn't a file
            return True
            
        change_detection = self.config.get('monitoring', {}).get('change_detection', {})
        method = change_detection.get('method', 'hash')
        
        if method == 'hash':
            # Get current file hash
            current_hash = self.compute_file_hash(path)
            if not current_hash:
                return True
                
            # Check if we have a cached hash
            cached_entry = self.file_cache.get(path, {})
            cached_hash = cached_entry.get('hash')
            
            if cached_hash and cached_hash == current_hash:
                # Update the timestamp but hash hasn't changed
                cached_entry['timestamp'] = time.time()
                self.file_cache[path] = cached_entry
                return False
            else:
                # Update cache with new hash
                self.file_cache[path] = {
                    'hash': current_hash,
                    'timestamp': time.time()
                }
                return True
        else:
            # Default to timestamp-based detection
            return True
    
    def process_event(self, event_type, path):
        """Process a file event"""
        # Skip this file if it should be ignored
        if os.path.isdir(path) and self.config.get('IGNORE_DIRECTORIES', True):
            return
            
        # Check for duplicate events (same file within dedup window)
        now = time.time()
        if path in self.last_seen:
            if now - self.last_seen[path] < self.dedup_window:
                logger.debug(f"Deduplicating event for {path}")
                return
        self.last_seen[path] = now
        
        # For created/modified events, check if content actually changed
        if event_type in ['created', 'modified'] and not self.has_file_changed(path):
            logger.debug(f"Skipping unchanged file: {path}")
            return
            
        # Queue the file for analysis
        logger.info(f"📝 File {event_type}: {path}")
        self.file_queue.put((event_type, path))