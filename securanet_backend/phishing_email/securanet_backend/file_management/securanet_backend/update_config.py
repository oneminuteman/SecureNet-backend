#!/usr/bin/env python
import os
import sys
import json
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securanet_backend.settings')
django.setup()

from django.conf import settings

def update_config():
    """Update the config file to set log retention values"""
    config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
    
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        return False
    
    try:
        # Load existing config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Update or add log retention settings
        if 'log_retention' not in config:
            config['log_retention'] = {}
        
        config['log_retention'].update({
            'max_records': 500,
            'auto_cleanup_enabled': True,
            'days_to_keep': 1,
            'cleanup_interval_hours': 6
        })
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Config updated with log retention settings")
        print("The following settings have been applied:")
        print("  - max_records: 500")
        print("  - auto_cleanup_enabled: True")
        print("  - days_to_keep: 1")
        print("  - cleanup_interval_hours: 6")
        
        return True
    
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

if __name__ == "__main__":
    update_config()