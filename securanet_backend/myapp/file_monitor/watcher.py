import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.utils import timezone
from ..models import FileChangeLog, FileAnalysis
from .ai_analyzer.analyzer import SecurityAnalyzer
import hashlib

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.analyzer = SecurityAnalyzer()
        super().__init__()

    def _get_dedup_key(self, path, event_type):
        current_time = timezone.now().timestamp()
        time_window = int(current_time / 5)  # 5-second window
        return hashlib.md5(f"{path}:{event_type}:{time_window}".encode()).hexdigest()

    def _analyze_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            metadata = {
                'analyzed_at': timezone.now().isoformat(),
                'analyzed_by': 'system'
            }
            
            result = self.analyzer.analyze_file(
                file_path=file_path,
                file_content=content,
                metadata=metadata
            )
            
            return result
        except Exception as e:
            print(f"Analysis failed for {file_path}: {str(e)}")
            return None

    def _handle_file_event(self, event, event_type):
        if event.is_directory:
            return

        dedup_key = self._get_dedup_key(event.src_path, event_type)
        
        # Check if we've recently processed this exact event
        if FileChangeLog.objects.filter(dedup_key=dedup_key).exists():
            return

        try:
            # Perform analysis
            analysis_result = self._analyze_file(event.src_path)
            
            if analysis_result:
                # Create FileAnalysis record
                file_analysis = FileAnalysis.objects.create(
                    file_path=event.src_path,
                    content_hash=analysis_result['file_info']['hash'],
                    risk_score=analysis_result['risk_analysis']['overall_score'],
                    risk_level=analysis_result['risk_analysis']['risk_level'],
                    analysis_result=analysis_result
                )
                
                # Create FileChangeLog record
                FileChangeLog.objects.create(
                    file_path=event.src_path,
                    change_type=event_type,
                    dedup_key=dedup_key,
                    analysis=file_analysis,
                    risk_level=analysis_result['risk_analysis']['risk_level'],
                    recommendation=analysis_result['recommendation']
                )
                
                print(f"✅ Analyzed and logged {event_type} event for {event.src_path}")
                print(f"Risk Level: {analysis_result['risk_analysis']['risk_level']}")
                print(f"Score: {analysis_result['risk_analysis']['overall_score']}")
            else:
                # Create a basic log if analysis fails
                FileChangeLog.objects.create(
                    file_path=event.src_path,
                    change_type=event_type,
                    dedup_key=dedup_key,
                    risk_level='unknown',
                    recommendation='Analysis failed. Manual review recommended.'
                )
                print(f"⚠️ Logged {event_type} event for {event.src_path} without analysis")
                
        except Exception as e:
            print(f"Error processing {event_type} event for {event.src_path}: {str(e)}")

    def on_created(self, event):
        self._handle_file_event(event, 'created')

    def on_modified(self, event):
        self._handle_file_event(event, 'modified')

    def on_deleted(self, event):
        self._handle_file_event(event, 'deleted')

class FileMonitor:
    def __init__(self, path_to_watch):
        self.path_to_watch = path_to_watch
        self.event_handler = FileEventHandler()
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.event_handler, self.path_to_watch, recursive=False)
        self.observer.start()
        print(f"🔍 Started monitoring: {self.path_to_watch}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        print("📥 Stopped monitoring")