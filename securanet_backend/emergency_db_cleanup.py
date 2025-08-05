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

def perform_emergency_cleanup():
    """Aggressively clean database to improve performance"""
    print("=" * 60)
    print("EMERGENCY DATABASE CLEANUP")
    print("=" * 60)
    print("Starting cleanup...")
    
    try:
        # Get current counts
        log_count = FileChangeLog.objects.count()
        analysis_count = FileAnalysis.objects.count()
        print(f"Current records: {log_count} logs, {analysis_count} analysis entries")
        
        # Keep only the most recent 100 records
        keep_count = 100
        
        # Delete excess logs
        if log_count > keep_count:
            # Get cutoff timestamp
            cutoff_log = FileChangeLog.objects.order_by('-timestamp')[keep_count-1:keep_count].first()
            if cutoff_log:
                # Delete older logs
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM myapp_filechangelog WHERE timestamp < %s",
                        [cutoff_log.timestamp]
                    )
                    deleted_logs = cursor.rowcount
                    print(f"Deleted {deleted_logs} old logs")
        
        # Delete excess analysis records
        if analysis_count > keep_count:
            # Determine timestamp field
            field_name = 'created_at' if hasattr(FileAnalysis, 'created_at') else 'timestamp'
            
            # Get cutoff record
            if field_name == 'created_at':
                cutoff = FileAnalysis.objects.order_by('-created_at')[keep_count-1:keep_count].first()
                if cutoff:
                    # Direct SQL for speed
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"DELETE FROM myapp_fileanalysis WHERE created_at < %s",
                            [cutoff.created_at]
                        )
                        deleted = cursor.rowcount
                        print(f"Deleted {deleted} old analysis records")
            else:
                cutoff = FileAnalysis.objects.order_by('-timestamp')[keep_count-1:keep_count].first()
                if cutoff:
                    # Direct SQL for speed
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"DELETE FROM myapp_fileanalysis WHERE timestamp < %s",
                            [cutoff.timestamp]
                        )
                        deleted = cursor.rowcount
                        print(f"Deleted {deleted} old analysis records")
        
        # Optimize database
        print("Optimizing database...")
        cursor = connection.cursor()
        cursor.execute("VACUUM")
        
        # Final counts
        final_log_count = FileChangeLog.objects.count()
        final_analysis_count = FileAnalysis.objects.count()
        
        print("\n" + "=" * 60)
        print("CLEANUP COMPLETED")
        print(f"Logs: {log_count} → {final_log_count}")
        print(f"Analysis: {analysis_count} → {final_analysis_count}")
        print("=" * 60)
        print("\n✅ Your system should now be responsive again.")
        print("Restart your server for the changes to take effect.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    perform_emergency_cleanup()