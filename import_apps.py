#!/usr/bin/env python3
"""
Script to import installed applications from .desktop files into the Tray Launcher configuration.
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from storage.config_manager import ConfigManager
from parser.desktop_parser import DesktopParser

def import_installed_applications():
    """
    Import all installed applications from .desktop files into the configuration.
    Also removes entries for applications that no longer exist.
    """
    config_manager = ConfigManager()
    desktop_parser = DesktopParser()
    
    print("Scanning for installed applications...")
    
    # Get all system applications
    system_apps = desktop_parser.scan_applications()
    
    print(f"Found {len(system_apps)} applications")
    
    # Add them to the config
    imported_count = 0
    for app in system_apps:
        # Add to a default category or organize by existing categories
        # For this example, we'll organize by the categories from the .desktop files
        categories = app.get('categories', ['Uncategorized'])
        
        # Add to each category specified in the .desktop file
        for category_name in categories:
            # Make the category name more user-friendly
            category_name = category_name.strip().title()
            if not category_name:  # If empty, use Uncategorized
                category_name = "Uncategorized"
            
            # Check if app already exists in config to avoid duplicates
            exists = False
            if category_name in config_manager.config['categories']:
                for existing_app in config_manager.config['categories'][category_name]:
                    if existing_app['name'] == app['name'] and existing_app['cmd'] == app['cmd']:
                        exists = True
                        break
            
            # Only add if it doesn't already exist
            if not exists:
                config_manager.add_application_to_category(category_name, app)
                imported_count += 1
                print(f"Added: {app['name']} to category '{category_name}'")
    
    # Clean up non-existent applications
    removed_count = remove_nonexistent_apps(config_manager)
    
    print(f"\nSuccessfully imported {imported_count} new applications!")
    if removed_count > 0:
        print(f"Removed {removed_count} non-existent applications!")
    print("Configuration updated.")


def check_executable_exists(executable):
    """
    Check if an executable exists in PATH or as absolute path.
    
    Args:
        executable (str): The executable name or path
        
    Returns:
        bool: True if executable exists, False otherwise
    """
    import os
    
    if os.path.isabs(executable):
        # Absolute path
        return os.path.isfile(executable) and os.access(executable, os.X_OK)
    else:
        # Search in PATH
        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            exe_path = os.path.join(path_dir, executable)
            if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                return True
        return False


def remove_nonexistent_apps(config_manager):
    """
    Remove applications from config that no longer exist on the system.
    Returns the number of removed applications.
    """
    removed_count = 0
    categories = config_manager.config['categories'].copy()
    
    for category_name, apps in categories.items():
        apps_to_remove = []
        
        for app in apps:
            cmd = app.get('cmd', '').strip()
            
            if not cmd:
                apps_to_remove.append(app)
                continue
            
            # Parse command to get the executable name
            import shlex
            try:
                cmd_parts = shlex.split(cmd)
                executable = cmd_parts[0]
            except:
                # If command parsing fails, mark for removal
                apps_to_remove.append(app)
                continue
            
            # Check if the executable exists in PATH or as absolute path
            if not check_executable_exists(executable):
                apps_to_remove.append(app)
        
        # Remove non-existent apps from this category
        for app in apps_to_remove:
            config_manager.remove_application_from_category(category_name, app['name'])
            removed_count += 1
    
    return removed_count

if __name__ == "__main__":
    import_installed_applications()