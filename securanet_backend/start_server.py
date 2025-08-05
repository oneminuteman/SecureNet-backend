import subprocess
import sys
import os
import time
import signal
import json

def load_config():
    """Load monitoring configuration"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monitor_config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        # Default config
        config = {
            'mode': 'custom',
            'paths': [os.path.expanduser('~/Documents')]
        }
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return config
        
def main():
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
    
    # Load config and set watch folder
    config = load_config()
    if config['paths']:
        os.environ['WATCH_FOLDER'] = config['paths'][0]
    
    print("Starting SecureNet Security Monitoring System")
    print("=" * 50)
    
    # Print configuration
    print(f"Monitoring mode: {config['mode']}")
    print("Monitored paths:")
    for path in config['paths']:
        print(f"  - {path}")
    print("-" * 50)
    
    processes = []
    
    try:
        # Start the Django server in a separate process
        print("Starting API server...")
        django_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver'
        ])
        processes.append(django_process)
        
        # Give Django server time to start
        time.sleep(2)
        
        # Start the file monitor in a separate process
        print("Starting file monitor...")
        monitor_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runmonitor'
        ])
        processes.append(monitor_process)
        
        print("\nSecureNet is running!")
        print("API: http://127.0.0.1:8000/api/")
        print("Press Ctrl+C to stop all services")
        
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