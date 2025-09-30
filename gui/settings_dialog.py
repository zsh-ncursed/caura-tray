import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SettingsDialog:
    """
    Settings dialog for Tray Launcher application.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the settings dialog.
        
        Args:
            config_manager (ConfigManager): Config manager to get and save settings
        """
        self.config_manager = config_manager
        
        # Get current settings
        settings = self.config_manager.config.get("settings", {})
        show_icons = settings.get("show_icons", True)
        
        # Create the dialog
        self.dialog = Gtk.Dialog(title="Settings", 
                                transient_for=None, 
                                flags=0,
                                buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        self.dialog.set_default_size(300, 100)
        
        # Create main box
        box = self.dialog.get_content_area()
        
        # Show icons toggle
        self.show_icons_toggle = Gtk.CheckButton(label="Show icons in menu")
        self.show_icons_toggle.set_active(show_icons)
        
        # Pack the widgets
        box.pack_start(self.show_icons_toggle, False, False, 10)
        
        # Show all widgets
        box.show_all()
    
    def run(self):
        """
        Run the settings dialog.
        
        Returns:
            bool: True if user clicked OK, False otherwise
        """
        response = self.dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Get selected values
            theme = self.theme_combo.get_active_id()
            show_icons = self.show_icons_toggle.get_active()
            
            # Update settings in config
            if "settings" not in self.config_manager.config:
                self.config_manager.config["settings"] = {}
            
            self.config_manager.config["settings"]["theme"] = theme
            self.config_manager.config["settings"]["show_icons"] = show_icons
            
            # Save the config
            self.config_manager.save_config()
        
        self.dialog.destroy()
        return response == Gtk.ResponseType.OK