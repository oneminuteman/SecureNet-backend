import subprocess
import sys
import os
import time
import signal
import json
import datetime
from pathlib import Path

def load_config():
    """Load monitoring configuration"""
    # Adjust path to look in the correct directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'ourapp', 'monitor_config.json')
    
    default_config = {
        'mode': 'custom',
        'paths': [os.path.expanduser('~/Documents'),
                  os.path.expanduser('~/Downloads'),
                  os.path.expanduser('~/Pictures')],
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    else:
        # Create default config
        config_dir = os.path.dirname(config_file)
        os.makedirs(config_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
        
def main():
    # Fix path to manage.py - look in the ourapp subdirectory
    manage_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ourapp', 'manage.py')
    
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ourapp.settings')
    
    # Load config and set watch folder
    config = load_config()
    paths = config.get('paths', [])
    
    # Ensure paths exist in config
    if not paths:
        print("⚠️ No paths configured for monitoring!")
        print("Adding default paths...")
        paths = [os.path.expanduser('~/Documents'), 
                 os.path.expanduser('~/Downloads')]
        config['paths'] = paths
        
        # Save updated config
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ourapp', 'monitor_config.json')
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Set first path as the WATCH_FOLDER (for backward compatibility)
    if paths:
        os.environ['WATCH_FOLDER'] = paths[0]
    
    print("\n✨ Starting SecureNet Security Monitoring System ✨")
    print("=" * 60)
    
    # Print configuration
    print(f"📋 Monitoring mode: {config.get('mode', 'custom')}")
    print("📂 Monitored paths:")
    for path in paths:
        path_exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {path_exists} {path}")
    print("-" * 60)
    
    processes = []
    
    try:
        # Check if manage.py exists
        if not os.path.exists(manage_py_path):
            print(f"❌ ERROR: manage.py not found at {manage_py_path}")
            print("Please check your project structure.")
            return
            
        # Start the Django server in a separate process
        print("🌐 Starting API server...")
        django_process = subprocess.Popen([
            sys.executable, manage_py_path, 'runserver'
        ])
        processes.append(django_process)
        
        # Give Django server time to start
        time.sleep(2)
        
        # Start the file monitor in a separate process
        print("🔍 Starting file monitor...")
        monitor_process = subprocess.Popen([
            sys.executable, manage_py_path, 'runmonitor',
            '--lightweight-startup'  # Start with lightweight monitoring
        ])
        processes.append(monitor_process)
        
        # Calculate full scan time
        scan_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        print("\n✅ SecureNet is running successfully!")
        print(f"API: http://127.0.0.1:8000/api/")
        print(f"Web Security: http://127.0.0.1:8000/websec/")
        print(f"ℹ️  Lightweight monitoring active now")
        print(f"🕒 Full system scan scheduled at: {scan_time.strftime('%H:%M:%S')}")
        print("\nPress Ctrl+C to stop all services")
        
        # Wait for both processes
        django_process.wait()
        monitor_process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down services...")
        for process in processes:
            try:
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:  # Linux/Mac
                    os.kill(process.pid, signal.SIGINT)
            except:
                pass
                
        # Give processes time to terminate gracefully
        time.sleep(1)
        
        # Force kill any remaining processes
        for process in processes:
            if process.poll() is None:  # Process is still running
                process.kill()
                
        print("Services stopped")
    except Exception as e:
        print(f"Error: {e}")
        for process in processes:
            process.terminate()
            
        print("Services stopped due to error")

if __name__ == '__main__':
    main()