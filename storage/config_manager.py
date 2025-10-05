import json
import os
import logging
from pathlib import Path

class ConfigManager:
    """
    Manages the configuration file for the Tray Launcher application.
    Handles loading, saving, and validation of the JSON configuration.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path (str, optional): Path to the config file. 
            If None, uses default path ~/.local/share/tray_launcher/config.json
        """
        if config_path is None:
            self.config_path = Path.home() / '.local' / 'share' / 'tray_launcher' / 'config.json'
        else:
            self.config_path = Path(config_path)
        
        # Ensure the config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize default config structure
        self.default_config = {
            "categories": {},
            "settings": {
                "show_icons": True,
                "show_quick_launch": True,
                "quick_launch_apps": {
                    "terminal": "x-terminal-emulator",
                    "browser": "x-www-browser", 
                    "file_manager": "xdg-open ~",
                    "mail_client": "xdg-email",
                    "messenger": "discord"  # или другой популярный мессенджер по умолчанию
                }
            }
        }
        
        # Callback for when config changes - allows notifying UI to update
        self.on_config_change = None
        
        # Load or create config
        self.config = self.load_config()
    
    def load_config(self):
        """
        Load configuration from the JSON file.
        
        Returns:
            dict: The loaded configuration or default config if file doesn't exist
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                    return self.validate_config(config)
            else:
                # Create default config if file doesn't exist
                self.save_config(self.default_config)
                return self.default_config
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error loading config: {e}")
            return self.default_config
        except Exception as e:
            logging.error(f"Unexpected error loading config: {e}")
            return self.default_config
    
    def validate_config(self, config):
        """
        Validate the configuration structure.
        
        Args:
            config (dict): The configuration to validate
            
        Returns:
            dict: Validated configuration (with defaults applied if needed)
        """
        if not isinstance(config, dict):
            logging.warning("Configuration is not a dictionary, using default")
            return self.default_config
        
        if "categories" not in config:
            config["categories"] = {}
        
        if not isinstance(config["categories"], dict):
            logging.warning("Categories in config are not a dictionary, using default")
            config["categories"] = {}
        
            # Remove theme setting since it's no longer used
            if "settings" in config and "theme" in config["settings"]:
                del config["settings"]["theme"]
            
            # Ensure quick launch settings exist
            if "settings" not in config:
                config["settings"] = {}
            
            settings = config["settings"]
            if "show_quick_launch" not in settings:
                settings["show_quick_launch"] = True
            
            if "quick_launch_apps" not in settings:
                settings["quick_launch_apps"] = {
                    "terminal": "x-terminal-emulator",
                    "browser": "x-www-browser", 
                    "file_manager": "xdg-open ~",
                    "mail_client": "xdg-email",
                    "messenger": "discord"
                }
            else:
                # Ensure all required quick launch apps are present
                quick_launch_defaults = {
                    "terminal": "x-terminal-emulator",
                    "browser": "x-www-browser", 
                    "file_manager": "xdg-open ~",
                    "mail_client": "xdg-email",
                    "messenger": "discord"
                }
                for key, default_value in quick_launch_defaults.items():
                    if key not in settings["quick_launch_apps"]:
                        settings["quick_launch_apps"][key] = default_value
            
        return config
    
    def save_config(self, config=None):
        """
        Save the configuration to the JSON file.
        
        Args:
            config (dict, optional): Config to save. If None, saves the current config
        """
        if config is None:
            config = self.config
            
        try:
            # Ensure the config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(config, file, ensure_ascii=False, indent=2)
                
            logging.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def add_application_to_category(self, category_name, app_info):
        """
        Add an application to a category in the configuration.
        
        Args:
            category_name (str): Name of the category
            app_info (dict): Application information with 'name' and 'cmd' keys
        """
        if category_name not in self.config["categories"]:
            self.config["categories"][category_name] = []
        
        # Check if the application already exists in the category
        for app in self.config["categories"][category_name]:
            if app.get('name') == app_info.get('name') and app.get('cmd') == app_info.get('cmd'):
                return  # App already exists
        
        self.config["categories"][category_name].append(app_info)
        self.save_config()
        
        # Notify that config has changed
        if self.on_config_change:
            self.on_config_change()
    
    def remove_application_from_category(self, category_name, app_name):
        """
        Remove an application from a category in the configuration.
        
        Args:
            category_name (str): Name of the category
            app_name (str): Name of the application to remove
        """
        if category_name in self.config["categories"]:
            self.config["categories"][category_name] = [
                app for app in self.config["categories"][category_name]
                if app.get('name') != app_name
            ]
            self.save_config()
            
            # Notify that config has changed
            if self.on_config_change:
                self.on_config_change()
    
    def get_all_applications(self):
        """
        Get all applications from all categories.
        
        Returns:
            dict: A dictionary with category names as keys and lists of applications as values
        """
        return self.config["categories"]
    
    def add_category(self, category_name):
        """
        Add a new category to the configuration.
        
        Args:
            category_name (str): Name of the category to add
        """
        if category_name not in self.config["categories"]:
            self.config["categories"][category_name] = []
            self.save_config()
            
            # Notify that config has changed
            if self.on_config_change:
                self.on_config_change()
    
    def remove_category(self, category_name):
        """
        Remove a category from the configuration.
        
        Args:
            category_name (str): Name of the category to remove
        """
        if category_name in self.config["categories"]:
            del self.config["categories"][category_name]
            self.save_config()
            
            # Notify that config has changed
            if self.on_config_change:
                self.on_config_change()
    
    def update_application(self, category_name, old_app_name, new_app_info):
        """
        Update an application in a category.
        
        Args:
            category_name (str): Name of the category
            old_app_name (str): Name of the application to update
            new_app_info (dict): Updated application information
        """
        if category_name in self.config["categories"]:
            for i, app in enumerate(self.config["categories"][category_name]):
                if app.get('name') == old_app_name:
                    self.config["categories"][category_name][i] = new_app_info
                    self.save_config()
                    
                    # Notify that config has changed
                    if self.on_config_change:
                        self.on_config_change()
                    break