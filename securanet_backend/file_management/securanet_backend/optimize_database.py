#!/usr/bin/env python
import os
import sys
import django
import sqlite3

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

from django.conf import settings
from django.db import connection

def optimize_database():
    """Optimize the SQLite database for better performance"""
    print("Optimizing database for better performance...")
    
    # Get database path
    db_path = settings.DATABASES['default']['NAME']
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return False
    
    print(f"Database file: {db_path}")
    original_size = os.path.getsize(db_path) / (1024*1024)
    print(f"Current size: {original_size:.2f} MB")
    
    # Close Django connection first
    connection.close()
    
    try:
        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run PRAGMA statements to optimize the database
        print("Applying optimizations:")
        
        cursor.execute("PRAGMA journal_mode = WAL;")
        print("✅ Set journal mode to WAL")
        
        cursor.execute("PRAGMA cache_size = 10000;")
        print("✅ Increased cache size")
        
        cursor.execute("PRAGMA temp_store = MEMORY;")
        print("✅ Set temporary storage to memory")
        
        cursor.execute("PRAGMA synchronous = NORMAL;")
        print("✅ Set synchronous mode to NORMAL")
        
        cursor.execute("PRAGMA mmap_size = 30000000;")
        print("✅ Set memory-mapped I/O")
        
        # Analyze tables for query optimization
        cursor.execute("ANALYZE;")
        print("✅ Analyzed tables for query optimization")
        
        # Run integrity check
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        if integrity_result == 'ok':
            print("✅ Database integrity check passed")
        else:
            print(f"⚠️ Database integrity check: {integrity_result}")
        
        # Vacuum the database to reclaim space
        print("\nVacuuming database (this may take a while)...")
        cursor.execute("VACUUM;")
        print("✅ Database vacuumed")
        
        # Close connection
        conn.close()
        
        # Report new size
        new_size = os.path.getsize(db_path) / (1024*1024)
        print(f"\nOperation completed successfully!")
        print(f"New database size: {new_size:.2f} MB")
        if new_size < original_size:
            print(f"Space saved: {(original_size - new_size):.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing database: {e}")
        return False

if __name__ == '__main__':
    if optimize_database():
        print("\n✅ Database optimization completed successfully")
        print("The log page should be much faster now")
    else:
        print("\n❌ Database optimization failed")