import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib, GdkPixbuf
import os
import subprocess
from pathlib import Path

class GtkTrayIcon:
    """
    Creates and manages the system tray icon using GTK+AppIndicator for the Tray Launcher application.
    This provides better support for icons in menus.
    """
    
    def __init__(self, on_open_launcher=None, on_settings=None, on_quit=None, 
                 config_manager=None, launcher_logic=None, desktop_parser=None):
        """
        Initialize the tray icon using AppIndicator.
        
        Args:
            on_open_launcher (function): Callback to open the launcher window
            on_settings (function): Callback for settings (not implemented yet)
            on_quit (function): Callback to quit the application
            config_manager (ConfigManager): Config manager to get application categories
            launcher_logic (ApplicationLauncher): Launcher logic to properly launch apps
            desktop_parser (DesktopParser): Desktop parser to scan applications
        """
        self.on_open_launcher = on_open_launcher
        self.on_settings = on_settings
        self.on_quit = on_quit
        self.config_manager = config_manager
        self.launcher_logic = launcher_logic
        self.desktop_parser = desktop_parser
        
        # Create the app indicator
        self.indicator = AppIndicator3.Indicator.new(
            "tray_launcher",
            "applications-system",  # Default icon name, will be updated later
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        
        # Set the status to active
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Create initial menu
        self.menu = self._create_menu()
        self.indicator.set_menu(self.menu)
    
    def _create_menu(self):
        """
        Create menu with categories and applications using GTK.
        """
        menu = Gtk.Menu()
        
        # Get all categories and applications from config
        categories = self.config_manager.get_all_applications() if self.config_manager else {}
        
        # Get settings
        settings = self.config_manager.config.get("settings", {})
        show_icons = settings.get("show_icons", True)
        show_quick_launch = settings.get("show_quick_launch", True)
        quick_launch_apps = settings.get("quick_launch_apps", {
            "terminal": "x-terminal-emulator",
            "browser": "x-www-browser",
            "file_manager": "xdg-open ~"
        })
        
        # Add quick launch applications at the top if enabled
        if show_quick_launch and quick_launch_apps:
            # Terminal quick launch
            if quick_launch_apps.get("terminal"):
                terminal_item = Gtk.ImageMenuItem()
                terminal_item.set_label("Terminal")
                
                if show_icons:
                    icon = Gtk.Image.new_from_icon_name("utilities-terminal", Gtk.IconSize.MENU)
                    terminal_item.set_image(icon)
                    terminal_item.set_always_show_image(True)
                
                terminal_item.connect("activate", self._on_app_launch, quick_launch_apps["terminal"])
                menu.append(terminal_item)
            
            # Browser quick launch
            if quick_launch_apps.get("browser"):
                browser_item = Gtk.ImageMenuItem()
                browser_item.set_label("Web Browser")
                
                if show_icons:
                    icon = Gtk.Image.new_from_icon_name("web-browser", Gtk.IconSize.MENU)
                    browser_item.set_image(icon)
                    browser_item.set_always_show_image(True)
                
                browser_item.connect("activate", self._on_app_launch, quick_launch_apps["browser"])
                menu.append(browser_item)
            
            # File manager quick launch
            if quick_launch_apps.get("file_manager"):
                fm_item = Gtk.ImageMenuItem()
                fm_item.set_label("File Manager")
                
                if show_icons:
                    icon = Gtk.Image.new_from_icon_name("system-file-manager", Gtk.IconSize.MENU)
                    fm_item.set_image(icon)
                    fm_item.set_always_show_image(True)
                
                fm_item.connect("activate", self._on_app_launch, quick_launch_apps["file_manager"])
                menu.append(fm_item)
            
            # Add separator after quick launch apps
            if quick_launch_apps.get("terminal") or quick_launch_apps.get("browser") or quick_launch_apps.get("file_manager"):
                separator = Gtk.SeparatorMenuItem()
                menu.append(separator)

        if categories:
            # Create menu items for each category
            for category_name, apps in categories.items():
                if not apps:  # Skip empty categories
                    continue
                
                # Define icon for category
                category_icon_name = self._get_category_icon(category_name)
                
                # Create a menu item for the category
                category_item = Gtk.ImageMenuItem()
                
                # Set the label for the category with app count
                category_item.set_label(f"{category_name} ({len(apps)})")
                
                # Set the icon for the category if show_icons is True
                if show_icons:
                    try:
                        # Try to load category icon
                        icon = Gtk.Image.new_from_icon_name(category_icon_name, Gtk.IconSize.MENU)
                        category_item.set_image(icon)
                        category_item.set_always_show_image(True)
                    except:
                        # If icon loading fails, just add a placeholder
                        icon = Gtk.Image.new_from_icon_name("folder", Gtk.IconSize.MENU)
                        category_item.set_image(icon)
                        category_item.set_always_show_image(True)
                
                # Create submenu for applications in this category
                submenu = Gtk.Menu()
                for app in apps:
                    app_name = app.get('name', 'Unknown')
                    app_cmd = app.get('cmd', '')
                    app_icon_path = app.get('icon', '')
                    
                    # Create menu item for the app
                    app_item = Gtk.ImageMenuItem()
                    
                    # Set the label for the app
                    app_item.set_label(app_name)
                    
                    # Set the icon for the app if show_icons is True
                    if show_icons:
                        icon_loaded = False
                        if app_icon_path:
                            try:
                                # First, try to load as an icon name from the theme
                                theme = Gtk.IconTheme.get_default()
                                # Check if the icon exists in the theme
                                if theme.has_icon(app_icon_path):
                                    app_item.set_image(Gtk.Image.new_from_icon_name(app_icon_path, Gtk.IconSize.MENU))
                                    icon_loaded = True
                                else:
                                    # Try common icon sizes and locations
                                    possible_paths = [
                                        f"/usr/share/icons/hicolor/16x16/apps/{app_icon_path}.png",
                                        f"/usr/share/icons/hicolor/24x24/apps/{app_icon_path}.png",
                                        f"/usr/share/icons/hicolor/32x32/apps/{app_icon_path}.png",
                                        f"/usr/share/icons/hicolor/48x48/apps/{app_icon_path}.png",
                                        f"/usr/share/icons/hicolor/64x64/apps/{app_icon_path}.png",
                                        f"/usr/share/icons/hicolor/scalable/apps/{app_icon_path}.svg",
                                        app_icon_path  # Original path
                                    ]
                                    
                                    for icon_path in possible_paths:
                                        if Path(icon_path).exists():
                                            try:
                                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 16, 16)
                                                app_item.set_image(Gtk.Image.new_from_pixbuf(pixbuf))
                                                icon_loaded = True
                                                break
                                            except:
                                                continue
                            except:
                                pass
                        
                        # If no icon was loaded or no icon path, use default
                        if not icon_loaded:
                            app_item.set_image(Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.MENU))
                        
                        # Force show the image
                        app_item.set_always_show_image(True)
                    
                    # Connect the activate signal to launch the application
                    app_item.connect("activate", self._on_app_launch, app_cmd)
                    submenu.append(app_item)
                
                # Set the submenu for the category item
                category_item.set_submenu(submenu)
                menu.append(category_item)
            
            # Add separator
            separator = Gtk.SeparatorMenuItem()
            menu.append(separator)
        
        # Add Regenerate menu item
        regenerate_item = Gtk.ImageMenuItem("Regenerate")
        if show_icons:
            regenerate_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.MENU)
            regenerate_item.set_image(regenerate_icon)
            regenerate_item.set_always_show_image(True)
        regenerate_item.connect("activate", self._on_regenerate)
        menu.append(regenerate_item)
        
        # Add Settings menu item
        settings_item = Gtk.ImageMenuItem("Settings")
        if show_icons:
            settings_icon = Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.MENU)
            settings_item.set_image(settings_icon)
            settings_item.set_always_show_image(True)
        settings_item.connect("activate", self._on_settings)
        menu.append(settings_item)
        
        # Add Quit menu item
        quit_item = Gtk.ImageMenuItem("Quit")
        if show_icons:
            quit_icon = Gtk.Image.new_from_icon_name("application-exit", Gtk.IconSize.MENU)
            quit_item.set_image(quit_icon)
            quit_item.set_always_show_image(True)
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)
        
        # Show all menu items
        menu.show_all()
        
        return menu
    
    def _get_category_icon(self, category_name):
        """
        Get appropriate icon name for a category.
        
        Args:
            category_name (str): Name of the category
            
        Returns:
            str: GTK icon name for the category
        """
        icon_mapping = {
            "General": "applications-accessories",
            "Development": "applications-development", 
            "Games": "applications-games",
            "Graphics": "applications-graphics",
            "Multimedia": "applications-multimedia",
            "Internet": "applications-internet",
            "Office": "applications-office",
            "Settings": "preferences-system",
            "System": "applications-system"
        }
        
        return icon_mapping.get(category_name, "application-x-executable")
    
    def _on_app_launch(self, widget, cmd):
        """
        Callback for launching an application.
        """
        if self.launcher_logic:
            # Use the proper launcher logic to validate and launch the application
            self.launcher_logic.launch_with_validation(cmd)
        else:
            # Fallback to basic launching if launcher_logic is not available
            try:
                # Split command safely, handling quoted arguments
                import shlex
                subprocess.Popen(shlex.split(cmd))
            except Exception as e:
                print(f"Error launching application: {e}")
    
    def _on_regenerate(self, widget):
        """
        Callback for the 'Regenerate' menu item.
        Scans for .desktop files and adds them to predefined categories.
        """
        if self.desktop_parser and self.config_manager:
            # Get all system applications organized by mapped categories
            categorized_apps = self.desktop_parser.get_applications_by_categories()
            
            # Add them to the config
            imported_count = 0
            for category_name, apps in categorized_apps.items():
                for app in apps:
                    # Check if app already exists in config to avoid duplicates
                    exists = False
                    if category_name in self.config_manager.config['categories']:
                        for existing_app in self.config_manager.config['categories'][category_name]:
                            if existing_app['name'] == app['name'] and existing_app['cmd'] == app['cmd']:
                                exists = True
                                break
                    
                    # Only add if it doesn't already exist
                    if not exists:
                        self.config_manager.add_application_to_category(category_name, app)
                        imported_count += 1
            
            if imported_count > 0:
                print(f"Added {imported_count} new applications from .desktop files")
                # Update the menu to show new apps
                self.update_menu()
            else:
                print("No new applications were found or all applications were already imported")
    
    def _on_settings(self, widget):
        """
        Callback for the 'Settings' menu item.
        """
        if self.on_settings:
            self.on_settings()
    
    def _on_quit(self, widget):
        """
        Callback for the 'Quit' menu item.
        """
        if self.on_quit:
            self.on_quit()
    
    def update_menu(self):
        """
        Update the menu with latest categories and applications.
        """
        # Remove old menu
        old_menu = self.indicator.get_menu()
        if old_menu:
            old_menu.destroy()
        
        # Create new menu
        new_menu = self._create_menu()
        self.indicator.set_menu(new_menu)
    
    def set_icon(self, icon_path):
        """
        Set the indicator icon.
        
        Args:
            icon_path (str): Path to the icon file
        """
        self.indicator.set_icon_full(icon_path, "Tray Launcher")
    
    def run(self):
        """
        Run the indicator (this is typically handled by the main GTK loop).
        """
        pass
    
    def run_detached(self):
        """
        Run the tray icon in a separate thread, allowing the main thread to continue.
        With GTK implementation, this doesn't run in a separate thread but is compatible
        with the expected interface.
        """
        # In GTK implementation, the tray icon is managed by the GTK main loop
        # so we return None to indicate it's managed differently
        return None