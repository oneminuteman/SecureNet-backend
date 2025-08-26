#!/usr/bin/env python
import os
import sys
import sqlite3
import time
import json

print("=" * 60)
print("SECURENET EMERGENCY RECOVERY")
print("=" * 60)
print("This script will aggressively clean up your database")
print("and restore system performance")
print("=" * 60)

# Get the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Find the database file
db_path = None
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.sqlite3'):
            db_path = os.path.join(root, file)
            break
    if db_path:
        break

if not db_path:
    print("❌ Could not find SQLite database file")
    sys.exit(1)

print(f"Found database: {db_path}")

# Connect directly to the database
try:
    print("Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current table sizes
    print("\nChecking current database status:")
    cursor.execute("SELECT COUNT(*) FROM myapp_filechangelog")
    log_count = cursor.fetchone()[0]
    print(f"Current log entries: {log_count}")
    
    cursor.execute("SELECT COUNT(*) FROM myapp_fileanalysis")
    analysis_count = cursor.fetchone()[0]
    print(f"Current analysis entries: {analysis_count}")
    
    # Ask for confirmation
    if log_count > 1000 or analysis_count > 1000:
        print("\n⚠️ WARNING: Your database has excessive logs!")
        print("This is likely causing your performance issues.")
        
    print("\nRecommended action: Keep only 100 most recent logs")
    confirm = input("Proceed with aggressive cleanup? (y/n): ").lower()
    
    if confirm != 'y':
        print("Operation cancelled")
        sys.exit(0)
    
    print("\n🔄 PERFORMING EMERGENCY CLEANUP")
    
    # DIRECT SQL APPROACH - much faster than ORM for large deletions
    keep_limit = 100  # Keep only 100 most recent entries
    
    # 1. Logs table
    start_time = time.time()
    print(f"Cleaning logs table (keeping {keep_limit} most recent entries)...")
    
    # Delete all except the most recent entries
    cursor.execute(f"""
        DELETE FROM myapp_filechangelog 
        WHERE id NOT IN (
            SELECT id FROM myapp_filechangelog 
            ORDER BY timestamp DESC 
            LIMIT {keep_limit}
        )
    """)
    deleted_logs = cursor.rowcount
    print(f"✅ Deleted {deleted_logs} log entries")
    
    # 2. Analysis table
    print(f"Cleaning analysis table (keeping {keep_limit} most recent entries)...")
    
    # Check which timestamp field is used
    cursor.execute("PRAGMA table_info(myapp_fileanalysis)")
    columns = [col[1] for col in cursor.fetchall()]
    timestamp_field = 'created_at' if 'created_at' in columns else 'timestamp'
    
    cursor.execute(f"""
        DELETE FROM myapp_fileanalysis 
        WHERE id NOT IN (
            SELECT id FROM myapp_fileanalysis 
            ORDER BY {timestamp_field} DESC 
            LIMIT {keep_limit}
        )
    """)
    deleted_analysis = cursor.rowcount
    print(f"✅ Deleted {deleted_analysis} analysis entries")
    
    # Commit changes
    conn.commit()
    
    # Optimize database
    print("Optimizing database (this may take a moment)...")
    cursor.execute("VACUUM")
    
    # Update config file to prevent this from happening again
    config_file = os.path.join(base_dir, 'monitor_config.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update log retention settings
            if 'log_retention' not in config:
                config['log_retention'] = {}
                
            config['log_retention'].update({
                'max_records': 100,
                'auto_cleanup_enabled': True,
                'days_to_keep': 1,
                'cleanup_interval_hours': 1
            })
            
            # If API settings exist, update them for better performance
            if 'api' not in config:
                config['api'] = {}
                
            config['api'].update({
                'max_logs_per_page': 50,
                'pagination_enabled': True
            })
            
            # Save changes
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            print("✅ Updated configuration with stricter log limits")
        except Exception as e:
            print(f"⚠️ Error updating config: {e}")
    
    # Final check
    cursor.execute("SELECT COUNT(*) FROM myapp_filechangelog")
    final_log_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM myapp_fileanalysis")
    final_analysis_count = cursor.fetchone()[0]
    
    # Close connection
    conn.close()
    
    duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("EMERGENCY RECOVERY COMPLETE")
    print("=" * 60)
    print(f"Logs: {log_count} → {final_log_count}")
    print(f"Analysis: {analysis_count} → {final_analysis_count}")
    print(f"Total removed: {log_count + analysis_count - final_log_count - final_analysis_count}")
    print(f"Operation completed in {duration:.2f} seconds")
    print("\n✅ YOUR SYSTEM SHOULD NOW BE RESPONSIVE AGAIN")
    print("\nNext steps:")
    print("1. Restart your server")
    print("2. Consider adding pagination to your API views")
    print("3. Check for unnecessary monitoring of high-churn folders")
    
except Exception as e:
    print(f"❌ Error during emergency recovery: {e}")
    import traceback
    traceback.print_exc()