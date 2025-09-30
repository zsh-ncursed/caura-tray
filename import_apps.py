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
    
    print(f"\nSuccessfully imported {imported_count} new applications!")
    print("Configuration updated.")

if __name__ == "__main__":
    import_installed_applications()