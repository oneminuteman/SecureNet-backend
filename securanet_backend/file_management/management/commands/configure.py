from django.core.management.base import BaseCommand
import os
import json
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Configure SecureNet monitoring settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset to default configuration',
        )

    def handle(self, *args, **options):
        config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
        
        if options['reset']:
            # Reset configuration
            self.create_default_config(config_file)
            self.stdout.write(self.style.SUCCESS('Configuration reset to defaults.'))
            return
            
        # Check if config file exists
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = self.create_default_config(config_file)
            
        # Get current settings
        current_mode = config.get('mode', 'custom')
        current_paths = config.get('paths', [])
        
        # Display current settings
        self.stdout.write(self.style.SUCCESS("\nSecureNet File Monitoring Configuration"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Current mode: {current_mode}")
        self.stdout.write("Currently monitored paths:")
        if current_paths:
            for path in current_paths:
                self.stdout.write(f"  - {path}")
        else:
            self.stdout.write("  (No paths configured)")
            
        # Prompt for mode change
        self.stdout.write("\nWould you like to monitor the entire system? (y/n) [default: n]: ")
        choice = input().strip().lower()
        if choice == 'y':
            config['mode'] = 'system-wide'
            config['paths'] = []
            
            # In system-wide mode, we'll monitor key directories
            home_dir = os.path.expanduser('~')
            config['paths'] = [
                home_dir,
                os.path.join(home_dir, 'Documents'),
                os.path.join(home_dir, 'Downloads')
            ]
            
            # Add other drives (Windows specific)
            if os.name == 'nt':
                import string
                from ctypes import windll
                
                drives = []
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        drives.append(f"{letter}:\\")
                    bitmask >>= 1
                
                self.stdout.write("\nDetected drives:")
                for i, drive in enumerate(drives):
                    self.stdout.write(f"{i+1}. {drive}")
                    
                self.stdout.write("\nSelect drives to monitor (comma-separated numbers, or 'all'): ")
                selection = input().strip()
                
                if selection.lower() == 'all':
                    selected_drives = drives
                else:
                    try:
                        indices = [int(x.strip()) - 1 for x in selection.split(',')]
                        selected_drives = [drives[i] for i in indices if 0 <= i < len(drives)]
                    except ValueError:
                        selected_drives = []
                
                for drive in selected_drives:
                    if drive not in config['paths']:
                        config['paths'].append(drive)
        else:
            config['mode'] = 'custom'
            
            # Allow user to modify paths
            self.stdout.write("\nCurrent paths:")
            if config['paths']:
                for i, path in enumerate(config['paths']):
                    self.stdout.write(f"{i+1}. {path}")
            else:
                self.stdout.write("  (No paths configured)")
                
            self.stdout.write("\nWould you like to add paths? (y/n) [default: y]: ")
            if input().strip().lower() != 'n':
                while True:
                    self.stdout.write("Enter path to monitor (or 'done' to finish): ")
                    path = input().strip()
                    if path.lower() == 'done':
                        break
                    
                    if os.path.exists(path):
                        if path not in config['paths']:
                            config['paths'].append(path)
                            self.stdout.write(self.style.SUCCESS(f"Added: {path}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"Path does not exist: {path}"))
            
            if config['paths']:
                self.stdout.write("\nWould you like to remove paths? (y/n) [default: n]: ")
                if input().strip().lower() == 'y':
                    self.stdout.write("\nSelect paths to remove (comma-separated numbers, or 'all'): ")
                    for i, path in enumerate(config['paths']):
                        self.stdout.write(f"{i+1}. {path}")
                    
                    selection = input().strip()
                    
                    if selection.lower() == 'all':
                        config['paths'] = []
                    else:
                        try:
                            indices = [int(x.strip()) - 1 for x in selection.split(',')]
                            for i in sorted(indices, reverse=True):
                                if 0 <= i < len(config['paths']):
                                    del config['paths'][i]
                        except ValueError:
                            pass
                
        # Update WATCH_FOLDER in settings if paths exist
        if config['paths']:
            # Use first path as primary watch folder
            os.environ['WATCH_FOLDER'] = config['paths'][0]
            
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.stdout.write(self.style.SUCCESS("\nConfiguration updated successfully."))
        self.stdout.write(self.style.SUCCESS("Restart the server for changes to take effect."))
        
    def create_default_config(self, config_file):
        """Create default configuration file"""
        config = {
            'mode': 'custom',
            'paths': [os.path.expanduser('~/Documents')],
            'excludes': [
                'C:/Windows',
                'C:/Program Files',
                'C:/Program Files (x86)'
            ]
        }
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config