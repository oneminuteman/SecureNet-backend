#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from myapp.models import FileChangeLog, FileAnalysis
from django.db import connection

def fix_and_run_cleanup():
    """Fix the cleanup and run it immediately"""
    print("Running fixed log cleanup...")
    
    try:
        # Define constants here to avoid variable scope issues
        max_records = 500  # Fixed value
        days_to_keep = 1   # Fixed value
        
        # Delete logs older than retention period
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        old_logs_deleted = FileChangeLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        print(f"Deleted {old_logs_deleted} logs older than {days_to_keep} days")
        
        # Check if FileAnalysis has created_at or timestamp
        if hasattr(FileAnalysis.objects.first(), 'created_at'):
            field_name = 'created_at'
        else:
            field_name = 'timestamp'
        
        # Delete old analysis records
        filter_kwargs = {f"{field_name}__lt": cutoff_date}
        old_analysis_deleted = FileAnalysis.objects.filter(**filter_kwargs).delete()[0]
        print(f"Deleted {old_analysis_deleted} analysis records older than {days_to_keep} days")
        
        # Limit to max_records
        current_logs = FileChangeLog.objects.count()
        if current_logs > max_records:
            # Get the timestamp of the cutoff log
            cutoff_log = FileChangeLog.objects.order_by('-timestamp')[max_records-1:max_records].first()
            if cutoff_log:
                excess_logs_deleted = FileChangeLog.objects.filter(timestamp__lt=cutoff_log.timestamp).delete()[0]
                print(f"Deleted {excess_logs_deleted} excess logs to maintain {max_records} limit")
        
        # Limit analysis records
        current_analysis = FileAnalysis.objects.count()
        if current_analysis > max_records:
            # Get the cutoff analysis record
            order_by = f"-{field_name}"
            cutoff_analysis = FileAnalysis.objects.order_by(order_by)[max_records-1:max_records].first()
            if cutoff_analysis:
                filter_kwargs = {f"{field_name}__lt": getattr(cutoff_analysis, field_name)}
                excess_analysis_deleted = FileAnalysis.objects.filter(**filter_kwargs).delete()[0]
                print(f"Deleted {excess_analysis_deleted} excess analysis records to maintain {max_records} limit")
        
        # Optimize database
        cursor = connection.cursor()
        cursor.execute('VACUUM;')
        print("Database optimized")
        
        # Final counts
        final_logs = FileChangeLog.objects.count()
        final_analysis = FileAnalysis.objects.count()
        
        print("\n" + "=" * 50)
        print(f"Fixed cleanup completed successfully")
        print(f"Current log count: {final_logs}")
        print(f"Current analysis record count: {final_analysis}")
        print(f"Total records: {final_logs + final_analysis}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during fixed cleanup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_and_run_cleanup()