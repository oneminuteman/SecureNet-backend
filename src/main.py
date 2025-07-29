# src/main.py
from monitor.config_manager import ConfigManager
from monitor.path_manager import PathManager
from monitor.setup_dialog import show_setup_dialog
from monitor.cli import cli
import os

def main():
    config_manager = ConfigManager()
    
    if config_manager.is_first_run():
        config = show_setup_dialog()
        config_manager.config['monitoring'].update(config)
        config_manager.save_config()
    
    path_manager = PathManager(config_manager)
    path_manager.start_monitoring()
    
    cli()

if __name__ == "__main__":
    main()