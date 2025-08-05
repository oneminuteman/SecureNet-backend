#!/usr/bin/env python
import os
import subprocess
import sys

def reset_database():
    """Reset the database completely and apply all migrations cleanly"""
    # Delete existing database
    db_path = os.path.join('db.sqlite3')
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
    
    # Apply migrations in correct order
    print("\n1. Applying core Django migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'auth'])
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'contenttypes'])
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'admin'])
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'sessions'])
    
    print("\n2. Applying myapp migrations...")
    # Create the FileChangeLog model with all required fields
    with open('myapp/models.py', 'r') as f:
        model_content = f.read()
    
    # Check if risk_level exists and add it if not
    if 'risk_level = models.CharField(' not in model_content:
        print("Adding risk_level field to FileChangeLog model...")
        new_content = model_content.replace(
            'class FileChangeLog(models.Model):',
            'class FileChangeLog(models.Model):\n'
            '    # Your existing fields here...\n'
            '    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index\n'
            '    file_path = models.TextField()\n'
            '    change_type = models.CharField(max_length=20)\n'
            '    risk_level = models.CharField(max_length=20, db_index=True, default="unknown")  # Add index\n'
            '    recommendation = models.TextField(null=True, blank=True)\n'
            '    dedup_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)\n'
        )
        with open('myapp/models.py', 'w') as f:
            f.write(new_content)
    
    # Create new migrations
    subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'myapp'])
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'myapp'])
    
    print("\n3. Applying securanet migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate', 'securanet'])
    
    # Create superuser
    print("\n4. Creating superuser...")
    subprocess.run([sys.executable, 'manage.py', 'createsuperuser'])
    
    print("\nDatabase reset complete. You can now start the server.")

if __name__ == '__main__':
    reset_database()