import os
import subprocess
import sys
import glob
import shutil

def reset_project():
    """Complete project reset to fix migration issues"""
    print("🔄 Starting complete project reset...")
    
    # Get the project directory - FIXING THE NESTED STRUCTURE ISSUE
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(base_dir, 'ourapp')  # The nested project directory
    
    print(f"📂 Base directory: {base_dir}")
    print(f"📂 Project directory: {project_dir}")
    
    if not os.path.exists(project_dir):
        print(f"❌ Error: Project directory {project_dir} does not exist!")
        return
        
    # 1. Delete the database
    db_path = os.path.join(project_dir, 'db.sqlite3')
    if os.path.exists(db_path):
        print(f"🗑️ Removing database: {db_path}")
        os.remove(db_path)
    else:
        print(f"ℹ️ No database found at: {db_path}")
    
    # 2. Remove all migrations except __init__.py
    apps = ['myapp', 'securanet']
    for app in apps:
        migration_dir = os.path.join(project_dir, app, 'migrations')
        if os.path.exists(migration_dir):
            print(f"🧹 Cleaning migrations in {app}...")
            
            # Create __init__.py if it doesn't exist
            init_file = os.path.join(migration_dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    pass
            
            # Remove all other migration files
            for migration_file in glob.glob(os.path.join(migration_dir, '*.py')):
                if os.path.basename(migration_file) != '__init__.py':
                    os.remove(migration_file)
        else:
            print(f"⚠️ Migration directory for {app} not found at: {migration_dir}")
    
    # 3. Make sure models are correctly defined
    print("📝 Checking models...")
    
    # Check if the models file exists
    models_path = os.path.join(project_dir, 'myapp', 'models.py')
    if not os.path.exists(models_path):
        print(f"❌ Error: Models file not found at: {models_path}")
        return
    
    # Ensure the FileChangeLog model has all required fields
    with open(models_path, 'r') as f:
        models_content = f.read()
    
    # Check if FileChangeLog exists
    if 'class FileChangeLog' in models_content:
        print("✅ FileChangeLog model found")
        
        # Parse the model
        start_idx = models_content.find('class FileChangeLog')
        end_idx = models_content.find('class', start_idx + 1)
        if end_idx == -1:
            end_idx = len(models_content)
        
        model_def = models_content[start_idx:end_idx]
        
        # Check for required fields
        required_fields = {
            'timestamp': 'models.DateTimeField(auto_now_add=True',
            'file_path': 'models.TextField(',
            'change_type': 'models.CharField(',
            'risk_level': 'models.CharField(max_length=20',
            'recommendation': 'models.TextField(null=True, blank=True)',
        }
        
        missing_fields = []
        for field, field_def in required_fields.items():
            if field_def not in model_def:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️ Missing fields in FileChangeLog: {', '.join(missing_fields)}")
            print("🔧 Adding missing fields...")
            
            new_model_def = model_def
            
            # Add timestamp if missing
            if 'timestamp' in missing_fields:
                new_model_def = new_model_def.replace(
                    'class FileChangeLog(models.Model):',
                    'class FileChangeLog(models.Model):\n    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)'
                )
            
            # Add file_path if missing
            if 'file_path' in missing_fields:
                new_model_def = new_model_def.replace(
                    'class FileChangeLog(models.Model):',
                    'class FileChangeLog(models.Model):\n    file_path = models.TextField()'
                )
            
            # Add change_type if missing
            if 'change_type' in missing_fields:
                new_model_def = new_model_def.replace(
                    'class FileChangeLog(models.Model):',
                    'class FileChangeLog(models.Model):\n    change_type = models.CharField(max_length=20)'
                )
            
            # Add risk_level if missing
            if 'risk_level' in missing_fields:
                new_model_def = new_model_def.replace(
                    'class FileChangeLog(models.Model):',
                    'class FileChangeLog(models.Model):\n    risk_level = models.CharField(max_length=20, db_index=True, default="unknown")'
                )
            
            # Add recommendation if missing
            if 'recommendation' in missing_fields:
                new_model_def = new_model_def.replace(
                    'class FileChangeLog(models.Model):',
                    'class FileChangeLog(models.Model):\n    recommendation = models.TextField(null=True, blank=True)'
                )
            
            # Replace the model definition in the file
            new_models_content = models_content.replace(model_def, new_model_def)
            
            with open(models_path, 'w') as f:
                f.write(new_models_content)
    else:
        print("❌ FileChangeLog model not found in models.py")
        return
    
    # 4. Create fresh migrations
    print("🔧 Creating fresh migrations...")
    subprocess.run([sys.executable, os.path.join(project_dir, 'manage.py'), 'makemigrations'], cwd=project_dir)
    
    # 5. Apply migrations
    print("🚀 Applying migrations...")
    subprocess.run([sys.executable, os.path.join(project_dir, 'manage.py'), 'migrate'], cwd=project_dir)
    
    # 6. Create superuser
    print("👤 Creating admin user...")
    subprocess.run([sys.executable, os.path.join(project_dir, 'manage.py'), 'createsuperuser'], cwd=project_dir)
    
    print("\n✅ Reset complete! You can now start the server with:")
    print("   python start_server.py")

if __name__ == '__main__':
    reset_project()