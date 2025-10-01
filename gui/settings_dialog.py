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
        
        self.dialog.set_default_size(500, 300)
        
        # Create main box
        box = self.dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_left(10)
        box.set_margin_right(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        
        # Show icons toggle
        self.show_icons_toggle = Gtk.CheckButton(label="Show icons in menu")
        self.show_icons_toggle.set_active(show_icons)
        
        # Show quick launch toggle
        self.show_quick_launch_toggle = Gtk.CheckButton(label="Show quick launch applications")
        self.show_quick_launch_toggle.set_active(settings.get("show_quick_launch", True))
        
        # Get quick launch app settings
        quick_launch_apps = settings.get("quick_launch_apps", {
            "terminal": "x-terminal-emulator",
            "browser": "x-www-browser", 
            "file_manager": "xdg-open ~"
        })
        
        # Terminal command entry
        terminal_label = Gtk.Label(label="Terminal command:")
        terminal_label.set_xalign(0)
        self.terminal_entry = Gtk.Entry()
        self.terminal_entry.set_text(quick_launch_apps.get("terminal", "x-terminal-emulator"))
        
        # Browser command entry
        browser_label = Gtk.Label(label="Browser command:")
        browser_label.set_xalign(0)
        self.browser_entry = Gtk.Entry()
        self.browser_entry.set_text(quick_launch_apps.get("browser", "x-www-browser"))
        
        # File manager command entry
        file_manager_label = Gtk.Label(label="File manager command:")
        file_manager_label.set_xalign(0)
        self.file_manager_entry = Gtk.Entry()
        self.file_manager_entry.set_text(quick_launch_apps.get("file_manager", "xdg-open ~"))
        
        # Pack the widgets
        box.pack_start(self.show_icons_toggle, False, False, 5)
        box.pack_start(self.show_quick_launch_toggle, False, False, 5)
        box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 5)
        box.pack_start(terminal_label, False, False, 5)
        box.pack_start(self.terminal_entry, False, False, 5)
        box.pack_start(browser_label, False, False, 5)
        box.pack_start(self.browser_entry, False, False, 5)
        box.pack_start(file_manager_label, False, False, 5)
        box.pack_start(self.file_manager_entry, False, False, 5)
        
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
            show_icons = self.show_icons_toggle.get_active()
            show_quick_launch = self.show_quick_launch_toggle.get_active()
            terminal_cmd = self.terminal_entry.get_text()
            browser_cmd = self.browser_entry.get_text()
            file_manager_cmd = self.file_manager_entry.get_text()
            
            # Update settings in config
            if "settings" not in self.config_manager.config:
                self.config_manager.config["settings"] = {}
            
            self.config_manager.config["settings"]["show_icons"] = show_icons
            self.config_manager.config["settings"]["show_quick_launch"] = show_quick_launch
            self.config_manager.config["settings"]["quick_launch_apps"] = {
                "terminal": terminal_cmd,
                "browser": browser_cmd,
                "file_manager": file_manager_cmd
            }
            
            # Save the config
            self.config_manager.save_config()
        
        self.dialog.destroy()
        return response == Gtk.ResponseType.OK