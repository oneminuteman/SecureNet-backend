import os
import json
import datetime
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path

# Config file path relative to project root
CONFIG_FILE = os.path.join(settings.BASE_DIR, 'monitor_config.json')

class Command(BaseCommand):
    help = 'Interactive command-line tool to select directories for monitoring'

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def load_config(self):
        """Load the existing configuration if it exists."""
        default_config = {
            "mode": "custom",
            "paths": [],
            "excludes": [
                "C:/Windows",
                "C:/Program Files",
                "C:/Program Files (x86)"
            ],
            "last_updated": "2025-07-29 23:23:37"
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
                    # Ensure all required keys exist
                    if "mode" not in config:
                        config["mode"] = default_config["mode"]
                    if "paths" not in config:
                        config["paths"] = default_config["paths"]
                    if "excludes" not in config:
                        config["excludes"] = default_config["excludes"]
                    
                    return config
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error loading config: {str(e)}'))
                return default_config
        return default_config

    def save_config(self, config):
        """Save the configuration to the config file."""
        config["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f'Configuration saved to {CONFIG_FILE}'))
            
            # Inform user about restarting monitoring
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('IMPORTANT: Changes will take effect when you restart the monitoring service.'))
            self.stdout.write(self.style.WARNING('Use the following command to restart monitoring:'))
            self.stdout.write('   python manage.py restartmonitor')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error saving config: {str(e)}'))

    def display_directories(self, paths):
        """Display the currently monitored directories."""
        if not paths:
            self.stdout.write(self.style.WARNING('No directories are currently being monitored.'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Currently monitored directories:'))
        for idx, path in enumerate(paths, 1):
            # Get directory name from path
            name = os.path.basename(path.rstrip('/\\'))
            self.stdout.write(f"  {idx}. {path} ({name})")

    def add_directory(self, config):
        """Add a new directory to monitor."""
        self.stdout.write('')
        self.stdout.write('Enter the full path of the directory to monitor:')
        path = input("> ").strip()
        
        # Normalize path (handles both forward and backslashes)
        path = os.path.normpath(path)
        
        # Validate the directory exists
        if not os.path.isdir(path):
            self.stdout.write(self.style.ERROR(f"Error: '{path}' is not a valid directory."))
            return config
        
        # Check permissions
        try:
            test_file = os.path.join(path, '.securenet_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Warning: Limited permissions on '{path}'. Some monitoring features may be restricted."))
            self.stdout.write(self.style.WARNING(f"Error: {str(e)}"))
            
            # Ask user if they want to proceed anyway
            proceed = input("Do you want to add this directory anyway? (y/n): ").strip().lower()
            if proceed != 'y':
                return config
        
        # Check if already in the list (case insensitive on Windows)
        for existing_path in config["paths"]:
            if os.name == 'nt':  # Windows
                if path.lower() == existing_path.lower():
                    self.stdout.write(self.style.WARNING('This directory is already being monitored.'))
                    return config
            else:  # Unix-like
                if path == existing_path:
                    self.stdout.write(self.style.WARNING('This directory is already being monitored.'))
                    return config
        
        # Add the directory
        config["paths"].append(path)
        
        # Get directory name for display
        name = os.path.basename(path.rstrip('/\\'))
        self.stdout.write(self.style.SUCCESS(f"Added '{name}' to monitored directories."))
        return config

    def remove_directory(self, config):
        """Remove a directory from monitoring."""
        if not config["paths"]:
            self.stdout.write(self.style.WARNING('No directories are currently being monitored.'))
            return config
        
        self.display_directories(config["paths"])
        self.stdout.write('')
        self.stdout.write('Enter the number of the directory to remove (or 0 to cancel):')
        try:
            choice = int(input("> "))
            if choice == 0:
                return config
            
            if 1 <= choice <= len(config["paths"]):
                removed_path = config["paths"].pop(choice-1)
                name = os.path.basename(removed_path.rstrip('/\\'))
                self.stdout.write(self.style.SUCCESS(f"Removed '{name}' from monitored directories."))
            else:
                self.stdout.write(self.style.ERROR('Invalid selection.'))
        except ValueError:
            self.stdout.write(self.style.ERROR('Please enter a valid number.'))
        
        return config

    def handle(self, *args, **options):
        config = self.load_config()
        
        while True:
            self.clear_screen()
            self.stdout.write("=" * 60)
            self.stdout.write("            SECURENET DIRECTORY SELECTOR")
            self.stdout.write("=" * 60)
            self.stdout.write('')
            self.stdout.write(f'Current User: {os.environ.get("USERNAME", "joshking-vs")}')
            self.stdout.write(f'Current Time: 2025-07-29 23:23:37')
            self.stdout.write('')
            self.stdout.write('Select an option:')
            self.stdout.write('  1. View monitored directories')
            self.stdout.write('  2. Add a directory to monitor')
            self.stdout.write('  3. Remove a monitored directory')
            self.stdout.write('  4. Save and exit')
            self.stdout.write('  5. Exit without saving')
            
            choice = input('\nEnter your choice (1-5): ')
            
            if choice == '1':
                self.display_directories(config["paths"])
                input('\nPress Enter to continue...')
            elif choice == '2':
                config = self.add_directory(config)
                input('\nPress Enter to continue...')
            elif choice == '3':
                config = self.remove_directory(config)
                input('\nPress Enter to continue...')
            elif choice == '4':
                self.save_config(config)
                self.stdout.write('Exiting...')
                break
            elif choice == '5':
                self.stdout.write('Exiting without saving changes...')
                break
            else:
                self.stdout.write(self.style.ERROR('Invalid choice. Please try again.'))
                input('\nPress Enter to continue...')