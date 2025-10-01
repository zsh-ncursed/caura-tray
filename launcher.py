#!/usr/bin/env python3
"""
Tray Launcher - A desktop launcher application for Linux with system tray integration.

This application provides:
- System tray icon with context menu
- Application launcher window with categorized apps
- Search functionality
- Import from .desktop files
- Configuration management
"""

import sys
import os
import signal
import threading
import logging
from pathlib import Path

# Initialize logging
log_file_path = Path.home() / '.local' / 'share' / 'tray_launcher' / 'tray_launcher.log'
log_file_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

# Add project modules to path
sys.path.insert(0, str(Path(__file__).parent))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from storage.config_manager import ConfigManager
from parser.desktop_parser import DesktopParser
from launcher_logic import ApplicationLauncher
from dbus_integration import DBusIntegration, initialize_dbus
from tray.gtk_tray_icon import GtkTrayIcon
from gui.main_window import MainWindow
from gui.dialogs import ErrorDialog


class TrayLauncherApp:
    """
    Main application class that ties all components together.
    """
    
    def __init__(self):
        """
        Initialize the Tray Launcher application.
        """
        # Initialize components
        self.config_manager = ConfigManager()
        self.desktop_parser = DesktopParser()
        self.launcher_logic = ApplicationLauncher()
        self.dbus_integration = DBusIntegration()
        
        # Initialize tray icon (needed for config change callback)
        self.tray_icon = GtkTrayIcon(
            on_open_launcher=self.toggle_main_window,
            on_settings=self.open_settings,
            on_quit=self.quit_application,
            config_manager=self.config_manager,
            launcher_logic=self.launcher_logic,
            desktop_parser=self.desktop_parser
        )
        
        # Set up the config change callback to update the tray menu
        self.config_manager.on_config_change = self.tray_icon.update_menu
        
        # Initialize main window (but don't show it yet)
        self.main_window = MainWindow(
            self.config_manager,
            self.desktop_parser,
            self.launcher_logic
        )
        
        # Initialize DBus
        initialize_dbus()
        
        # Track application state
        self.is_running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def toggle_main_window(self):
        """
        Toggle the visibility of the main window.
        """
        try:
            self.main_window.toggle_visibility()
        except Exception as e:
            logging.error(f"Error toggling main window: {e}")
            ErrorDialog.show(None, f"Error toggling main window: {e}")
    
    def open_settings(self):
        """
        Open settings dialog.
        """
        logging.info("Settings requested")
        
        # Import here to avoid circular imports
        from gui.settings_dialog import SettingsDialog
        
        # Get old settings to check if they change
        old_settings = self.config_manager.config.get("settings", {}).copy()
        
        # Create and run the settings dialog
        dialog = SettingsDialog(self.config_manager)
        dialog.run()
        
        # Check if settings have changed
        new_settings = self.config_manager.config.get("settings", {})
        if old_settings != new_settings:
            # If settings changed, update the tray menu
            self.config_manager.on_config_change()
    
    def quit_application(self):
        """
        Quit the application gracefully.
        """
        logging.info("Quitting application")
        self.is_running = False
        
        # Hide main window
        try:
            self.main_window.hide()
        except:
            pass
        
        # Stop tray icon
        try:
            self.tray_icon.stop()
        except:
            pass
        
        # Exit the application
        os._exit(0)  # Force exit since the tray icon thread might prevent normal exit
    
    def signal_handler(self, signum, frame):
        """
        Handle system signals for graceful shutdown.
        """
        logging.info(f"Received signal {signum}, shutting down...")
        self.quit_application()
    
    def run(self):
        """
        Run the Tray Launcher application.
        """
        logging.info("Starting Tray Launcher application")
        
        try:
            # Initialize the tray icon (GTK implementation is managed by the main GTK loop)
            # No need to run in a separate thread for GTK implementation
            
            # Start the main GTK loop
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, GObject
            
            # Handle quit properly
            def gtk_quit_handler():
                self.quit_application()
                return False  # Don't repeat
            
            # Connect the GTK quit handler
            Gtk.main()
            
        except KeyboardInterrupt:
            logging.info("Application interrupted by user")
            self.quit_application()
        except Exception as e:
            logging.error(f"Error running application: {e}")
            ErrorDialog.show(None, f"Error running application: {e}")
            self.quit_application()


def main():
    """
    Main entry point for the application.
    """
    # Create and run the Tray Launcher application
    app = TrayLauncherApp()
    app.run()


if __name__ == "__main__":
    main()