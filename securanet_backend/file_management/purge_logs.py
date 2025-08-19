#!/usr/bin/env python
import os
import sys
import django
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

from django.db import connection
from myapp.models import FileChangeLog, FileAnalysis

def purge_logs(keep_count=500):
    """Aggressively purge logs to keep only the specified number"""
    start_time = time.time()
    print(f"Starting aggressive log purge. Will keep only {keep_count} most recent logs.")
    
    try:
        # Get current counts
        log_count = FileChangeLog.objects.count()
        analysis_count = FileAnalysis.objects.count()
        print(f"Current counts: {log_count} logs, {analysis_count} analysis records")
        
        if log_count <= keep_count:
            print(f"Log count ({log_count}) is already below limit ({keep_count}). No action needed.")
        else:
            # Get the timestamp of the cutoff log
            cutoff_log = FileChangeLog.objects.order_by('-timestamp')[keep_count-1:keep_count].first()
            if cutoff_log:
                cutoff_time = cutoff_log.timestamp
                print(f"Cutoff timestamp: {cutoff_time}")
                
                # Delete all logs older than the cutoff
                deleted_count = FileChangeLog.objects.filter(timestamp__lt=cutoff_time).delete()[0]
                print(f"✅ Deleted {deleted_count} logs")
            else:
                print("Could not determine cutoff log.")
        
        # Handle analysis records
        if analysis_count <= keep_count:
            print(f"Analysis count ({analysis_count}) is already below limit ({keep_count}). No action needed.")
        else:
            # Check field name (created_at or timestamp)
            field_name = 'created_at' if hasattr(FileAnalysis, 'created_at') else 'timestamp'
            
            # Get the cutoff analysis record
            if field_name == 'created_at':
                cutoff_analysis = FileAnalysis.objects.order_by('-created_at')[keep_count-1:keep_count].first()
                if cutoff_analysis:
                    cutoff_time = cutoff_analysis.created_at
                    print(f"Analysis cutoff timestamp: {cutoff_time}")
                    deleted_count = FileAnalysis.objects.filter(created_at__lt=cutoff_time).delete()[0]
                    print(f"✅ Deleted {deleted_count} analysis records")
            else:
                cutoff_analysis = FileAnalysis.objects.order_by('-timestamp')[keep_count-1:keep_count].first()
                if cutoff_analysis:
                    cutoff_time = cutoff_analysis.timestamp
                    print(f"Analysis cutoff timestamp: {cutoff_time}")
                    deleted_count = FileAnalysis.objects.filter(timestamp__lt=cutoff_time).delete()[0]
                    print(f"✅ Deleted {deleted_count} analysis records")
        
        # Optimize database
        print("Optimizing database...")
        cursor = connection.cursor()
        cursor.execute('VACUUM;')
        print("✅ Database optimized")
        
        # Final counts
        final_log_count = FileChangeLog.objects.count()
        final_analysis_count = FileAnalysis.objects.count()
        
        print("\n" + "=" * 50)
        print(f"Purge completed in {time.time() - start_time:.2f} seconds")
        print(f"Logs: {log_count} → {final_log_count} (removed {log_count - final_log_count})")
        print(f"Analysis: {analysis_count} → {final_analysis_count} (removed {analysis_count - final_analysis_count})")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during log purge: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Default to keeping 500 most recent logs
    keep_count = 500
    
    # Check if a custom count was provided
    if len(sys.argv) > 1:
        try:
            keep_count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}. Using default: {keep_count}")
    
    purge_logs(keep_count)