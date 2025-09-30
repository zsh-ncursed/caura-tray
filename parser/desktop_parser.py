import os
import re
from pathlib import Path
import logging
from typing import List, Dict, Optional

class DesktopParser:
    """
    Parses .desktop files to extract application information.
    """
    
    def __init__(self):
        self.system_app_paths = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            Path.home() / ".local/share/applications"
        ]
    
    def clean_exec_command(self, exec_cmd: str) -> str:
        """
        Clean the Exec command by removing placeholders like %U, %f, etc.
        
        Args:
            exec_cmd (str): The original Exec command from the .desktop file
            
        Returns:
            str: Cleaned command without placeholders
        """
        if not exec_cmd:
            return exec_cmd
        
        # Remove common placeholders used in .desktop files
        # List of common placeholders in .desktop files
        placeholders = [
            r'%U',  # URL
            r'%u',  # URL (single)
            r'%F',  # Files
            r'%f',  # File (single)
            r'%D',  # Directory
            r'%d',  # Directory (single)
            r'%N',  # Basename
            r'%n',  # Basename (single)
            r'%i',  # Icon
            r'%c',  # Name
            r'%k',  # Location
            r'%v',  # Device
            r'%m',  # Window manager
            r'%M',  # Menu item id
        ]
        
        cleaned_cmd = exec_cmd
        for placeholder in placeholders:
            cleaned_cmd = re.sub(placeholder, '', cleaned_cmd)
        
        # Remove any extra spaces that might have been left after removing placeholders
        cleaned_cmd = ' '.join(cleaned_cmd.split())
        
        return cleaned_cmd.strip()
    
    def parse_desktop_file(self, file_path: str) -> Optional[Dict[str, any]]:
        """
        Parse a single .desktop file and extract application information.
        
        Args:
            file_path (str): Path to the .desktop file
            
        Returns:
            dict or None: Dictionary with application information (name, cmd, icon, categories) or None if parsing fails
        """
        try:
            app_info = {
                "name": "",
                "cmd": "",
                "icon": "",
                "nodisplay": False,
                "categories": []
            }
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Split content into lines
            lines = content.split('\n')
            
            # Flag to determine if we're in the [Desktop Entry] section
            in_desktop_entry = False
            
            for line in lines:
                line = line.strip()
                
                # Check for section header
                if line.startswith('[') and line.endswith(']'):
                    in_desktop_entry = line.lower() == '[desktop entry]'
                    continue
                
                # Only process lines in the Desktop Entry section
                if not in_desktop_entry:
                    continue
                
                # Skip comments
                if line.startswith('#') or not line:
                    continue
                
                # Parse key-value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle quoted values
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith('\'') and value.endswith('\''):
                        value = value[1:-1]
                    
                    # Extract relevant information
                    if key.lower() == 'name':
                        app_info['name'] = value
                    elif key.lower() == 'exec':
                        app_info['cmd'] = self.clean_exec_command(value)
                    elif key.lower() == 'icon':
                        app_info['icon'] = value
                    elif key.lower() == 'nodisplay':
                        app_info['nodisplay'] = value.lower() in ('true', 'yes', '1')
                    elif key.lower() == 'categories':
                        # Parse categories (they are usually comma-separated)
                        categories = [cat.strip().title() for cat in value.split(';') if cat.strip()]
                        app_info['categories'] = categories
            
            # Only return info if we have both name and command
            if app_info['name'] and app_info['cmd']:
                # Don't return apps that are marked as NoDisplay
                if not app_info['nodisplay']:
                    # If no categories were found, use 'Uncategorized'
                    if not app_info['categories']:
                        app_info['categories'] = ['Uncategorized']
                    return app_info
            
            return None
            
        except Exception as e:
            logging.error(f"Error parsing .desktop file {file_path}: {e}")
            return None
    
    def find_desktop_files(self) -> List[str]:
        """
        Find all .desktop files in standard locations.
        
        Returns:
            list: List of paths to .desktop files
        """
        desktop_files = []
        
        for path in self.system_app_paths:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_dir():
                # Find all .desktop files in the directory
                for desktop_file in path_obj.glob("*.desktop"):
                    desktop_files.append(str(desktop_file))
        
        return desktop_files
    
    def scan_applications(self) -> List[Dict[str, str]]:
        """
        Scan system directories for .desktop files and parse them.
        
        Returns:
            list: List of dictionaries with parsed application information
        """
        all_apps = []
        
        desktop_files = self.find_desktop_files()
        
        for desktop_file in desktop_files:
            app_info = self.parse_desktop_file(desktop_file)
            if app_info:
                all_apps.append(app_info)
        
        return all_apps

    def map_categories(self, app_categories: List[str]) -> str:
        """
        Map the categories from the .desktop file to our predefined categories.
        Each application will be assigned to only one category based on priority.
        
        Args:
            app_categories (List[str]): List of categories from the .desktop file
            
        Returns:
            str: The mapped category name
        """
        # Define our fixed categories and their corresponding keywords
        category_keywords = {
            "System": ["system", "settings", "preferences", "configure", "admin", "hardware"],
            "Settings": ["settings", "preferences", "configure", "control"],
            "Office": ["office", "word", "spreadsheet", "document", "text", "edit", "publish"],
            "Graphics": ["graphics", "2dgraphics", "3dgraphics", "image", "photo", "picture", "art"],
            "Multimedia": ["audio", "audiovideo", "music", "video", "tv", "player", "recorder"],
            "Internet": ["network", "email", "web", "internet", "chat", "p2p", "filetransfer"],
            "Games": ["game", "arcade", "sports", "kids", "logic", "strategy", "simulation"],
            "Development": ["development", "programming", "ide", "editor", "debugger", "database"],
            "General": ["utility", "accessibility", "archiving", "calculator", "clock", "filemanager"]
        }
        
        # Convert to lowercase for comparison
        app_categories_lower = [cat.lower() for cat in app_categories]
        
        # Check each predefined category in priority order
        for main_category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in app_categories_lower:
                    return main_category
        
        # If no match found, return 'General' as default
        return "General"
    
    def get_applications_by_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Scan applications and organize them by our predefined categories.
        Each application will be assigned to only one category.
        
        Returns:
            dict: Dictionary with category names as keys and lists of applications as values
        """
        apps = self.scan_applications()
        
        # Predefined categories
        predefined_categories = {
            "General": [],
            "Development": [],
            "Games": [],
            "Graphics": [],
            "Multimedia": [],
            "Internet": [],
            "Office": [],
            "Settings": [],
            "System": []
        }
        
        # Assign each app to only one category based on mapping
        for app in apps:
            categories = app.get('categories', [])
            mapped_category = self.map_categories(categories)
            
            # Add the app to the mapped category
            if mapped_category in predefined_categories:
                predefined_categories[mapped_category].append(app)
            else:
                # If the category is not in our predefined list, add to 'General'
                predefined_categories["General"].append(app)
        
        return predefined_categories