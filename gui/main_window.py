import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango
import subprocess
import threading
import logging
from pathlib import Path

class MainWindow:
    """
    Main window for the Tray Launcher application with search and categories.
    """
    
    def __init__(self, config_manager, desktop_parser, launcher_logic):
        """
        Initialize the main window.
        
        Args:
            config_manager (ConfigManager): Configuration manager instance
            desktop_parser (DesktopParser): Desktop parser instance
            launcher_logic (ApplicationLauncher): Application launcher instance
        """
        self.config_manager = config_manager
        self.desktop_parser = desktop_parser
        self.launcher_logic = launcher_logic
        
        # Window setup
        self.window = Gtk.Window(title="Tray Launcher")
        self.window.set_default_size(600, 500)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Connect the window close event
        self.window.connect("destroy", self.on_window_close)
        
        # Main vertical box
        main_box = Gtk.VBox(spacing=10)
        self.window.add(main_box)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search applications...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        main_box.pack_start(self.search_entry, False, False, 0)
        
        # Create scrolled window for the application list
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scrolled_window, True, True, 0)
        
        # Create a list box for categories and applications
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window.add(self.list_box)
        
        # Create buttons box
        buttons_box = Gtk.HBox(spacing=5)
        buttons_box.set_border_width(10)
        
        # Regenerate button (import .desktop files)
        self.regenerate_button = Gtk.Button(label="Regenerate")
        self.regenerate_button.connect("clicked", self.on_regenerate_clicked)
        buttons_box.pack_start(self.regenerate_button, False, False, 0)
        
        # Edit config button
        self.edit_config_button = Gtk.Button(label="Edit Config")
        self.edit_config_button.connect("clicked", self.on_edit_config_clicked)
        buttons_box.pack_start(self.edit_config_button, False, False, 0)
        
        # Quit button
        self.quit_button = Gtk.Button(label="Quit")
        self.quit_button.connect("clicked", self.on_quit_clicked)
        buttons_box.pack_end(self.quit_button, False, False, 0)
        
        main_box.pack_start(buttons_box, False, False, 0)
        
        # Store the original applications data
        self.original_apps = {}
        
        # Current search text for filtering
        self.current_search = ""
        
        # Refresh the display
        self.refresh_display()
    
    def on_window_close(self, widget):
        """
        Handle the window close event by hiding the window instead of destroying it.
        """
        self.window.hide()
        return True  # Return True to prevent actual destruction
    
    def refresh_display(self):
        """
        Refresh the display with current applications from the config.
        """
        # Clear the current list box
        for child in self.list_box.get_children():
            self.list_box.remove(child)
        
        # Get applications from config
        self.original_apps = self.config_manager.get_all_applications()
        
        # Get settings
        settings = self.config_manager.config.get("settings", {})
        show_quick_launch = settings.get("show_quick_launch", True)
        quick_launch_apps = settings.get("quick_launch_apps", {
            "terminal": "x-terminal-emulator",
            "browser": "x-www-browser",
            "file_manager": "xdg-open ~",
            "mail_client": "xdg-email",
            "messenger": "discord"
        })
        
        # Add quick launch applications at the top if enabled
        if show_quick_launch and any(quick_launch_apps.values()):
            # Create a section for quick launch apps
            quick_launch_expander = Gtk.Expander()
            quick_launch_expander.set_label("Quick Launch")
            
            # Create a vertical box to hold the quick launch apps
            quick_launch_vbox = Gtk.VBox()
            
            # Terminal quick launch
            if quick_launch_apps.get("terminal"):
                hbox = Gtk.HBox()
                label = Gtk.Label(label="Terminal")
                label.set_xalign(0)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                hbox.pack_start(label, True, True, 5)
                
                btn = Gtk.Button(label="Launch")
                btn.connect("clicked", self.on_launch_app, quick_launch_apps["terminal"])
                hbox.pack_end(btn, False, False, 5)
                
                quick_launch_vbox.pack_start(hbox, False, False, 2)
            
            # Browser quick launch
            if quick_launch_apps.get("browser"):
                hbox = Gtk.HBox()
                label = Gtk.Label(label="Web Browser")
                label.set_xalign(0)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                hbox.pack_start(label, True, True, 5)
                
                btn = Gtk.Button(label="Launch")
                btn.connect("clicked", self.on_launch_app, quick_launch_apps["browser"])
                hbox.pack_end(btn, False, False, 5)
                
                quick_launch_vbox.pack_start(hbox, False, False, 2)
            
            # File manager quick launch
            if quick_launch_apps.get("file_manager"):
                hbox = Gtk.HBox()
                label = Gtk.Label(label="File Manager")
                label.set_xalign(0)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                hbox.pack_start(label, True, True, 5)
                
                btn = Gtk.Button(label="Launch")
                btn.connect("clicked", self.on_launch_app, quick_launch_apps["file_manager"])
                hbox.pack_end(btn, False, False, 5)
                
                quick_launch_vbox.pack_start(hbox, False, False, 2)
            
            # Mail client quick launch
            if quick_launch_apps.get("mail_client"):
                hbox = Gtk.HBox()
                label = Gtk.Label(label="Mail Client")
                label.set_xalign(0)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                hbox.pack_start(label, True, True, 5)
                
                btn = Gtk.Button(label="Launch")
                btn.connect("clicked", self.on_launch_app, quick_launch_apps["mail_client"])
                hbox.pack_end(btn, False, False, 5)
                
                quick_launch_vbox.pack_start(hbox, False, False, 2)
            
            # Messenger quick launch
            if quick_launch_apps.get("messenger"):
                hbox = Gtk.HBox()
                label = Gtk.Label(label="Messenger")
                label.set_xalign(0)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                hbox.pack_start(label, True, True, 5)
                
                btn = Gtk.Button(label="Launch")
                btn.connect("clicked", self.on_launch_app, quick_launch_apps["messenger"])
                hbox.pack_end(btn, False, False, 5)
                
                quick_launch_vbox.pack_start(hbox, False, False, 2)
            
            quick_launch_expander.add(quick_launch_vbox)
            self.list_box.add(quick_launch_expander)
        
        # If there's a current search, show search results only
        if self.current_search:
            self.show_search_results()
        else:
            # Show applications organized by categories
            self.show_categories()
    
    def show_categories(self):
        """
        Show applications organized by categories.
        """
        categories = self.original_apps
        
        for category_name, apps in categories.items():
            if not apps:  # Skip empty categories
                continue
            
            # Create expander for the category
            expander = Gtk.Expander()
            expander.set_label(f"{category_name} ({len(apps)})")  # Show count of apps
            
            # Create a vertical box to hold the application buttons
            vbox = Gtk.VBox()
            expander.add(vbox)
            
            for app in apps:
                # Create a horizontal box for each app with name and launch button
                hbox = Gtk.HBox()
                
                # App name label
                label = Gtk.Label(label=app['name'])
                label.set_xalign(0)  # Left align
                label.set_ellipsize(Pango.EllipsizeMode.END)  # Ellipsize long names
                hbox.pack_start(label, True, True, 5)
                
                # Launch button
                btn = Gtk.Button(label="Launch")
                btn.connect("clicked", self.on_launch_app, app['cmd'])
                hbox.pack_end(btn, False, False, 5)
                
                # Add the horizontal box to the category's vertical box
                vbox.pack_start(hbox, False, False, 2)
            
            # Add the expander to the list box
            self.list_box.add(expander)
        
        # Show all widgets
        self.list_box.show_all()
    
    def show_search_results(self):
        """
        Show search results across all categories.
        """
        search_term = self.current_search.lower()
        matched_apps = []
        
        # Get quick launch apps for search
        settings = self.config_manager.config.get("settings", {})
        show_quick_launch = settings.get("show_quick_launch", True)
        quick_launch_apps = settings.get("quick_launch_apps", {
            "terminal": "x-terminal-emulator",
            "browser": "x-www-browser",
            "file_manager": "xdg-open ~"
        })
        
        # Check quick launch apps for matches if enabled
        quick_launch_matches = []
        if show_quick_launch:
            if quick_launch_apps.get("terminal") and search_term in "terminal".lower():
                quick_launch_matches.append(("Quick Launch", {
                    'name': 'Terminal',
                    'cmd': quick_launch_apps["terminal"]
                }))
            if quick_launch_apps.get("browser") and search_term in "web browser".lower():
                quick_launch_matches.append(("Quick Launch", {
                    'name': 'Web Browser',
                    'cmd': quick_launch_apps["browser"]
                }))
            if quick_launch_apps.get("file_manager") and search_term in "file manager".lower():
                quick_launch_matches.append(("Quick Launch", {
                    'name': 'File Manager',
                    'cmd': quick_launch_apps["file_manager"]
                }))
            if quick_launch_apps.get("mail_client") and search_term in "mail client".lower():
                quick_launch_matches.append(("Quick Launch", {
                    'name': 'Mail Client',
                    'cmd': quick_launch_apps["mail_client"]
                }))
            if quick_launch_apps.get("messenger") and search_term in "messenger".lower():
                quick_launch_matches.append(("Quick Launch", {
                    'name': 'Messenger',
                    'cmd': quick_launch_apps["messenger"]
                }))

        for category_name, apps in self.original_apps.items():
            for app in apps:
                if (search_term in app['name'].lower() or 
                    search_term in app['cmd'].lower()):
                    matched_apps.append((category_name, app))
        
        # Add quick launch matches first
        for category_name, app in quick_launch_matches:
            # Create a horizontal box for each app with name and launch button
            hbox = Gtk.HBox()
            
            # App name label with category info
            label = Gtk.Label(label=f"{app['name']} ({category_name})")
            label.set_xalign(0)  # Left align
            label.set_ellipsize(Pango.EllipsizeMode.END)  # Ellipsize long names
            hbox.pack_start(label, True, True, 5)
            
            # Launch button
            btn = Gtk.Button(label="Launch")
            btn.connect("clicked", self.on_launch_app, app['cmd'])
            hbox.pack_end(btn, False, False, 5)
            
            # Add the horizontal box to the list box
            self.list_box.add(hbox)
        
        # Add matched apps to the list box
        for category_name, app in matched_apps:
            # Create a horizontal box for each app with name and launch button
            hbox = Gtk.HBox()
            
            # App name label with category info
            label = Gtk.Label(label=f"{app['name']} ({category_name})")
            label.set_xalign(0)  # Left align
            label.set_ellipsize(Pango.EllipsizeMode.END)  # Ellipsize long names
            hbox.pack_start(label, True, True, 5)
            
            # Launch button
            btn = Gtk.Button(label="Launch")
            btn.connect("clicked", self.on_launch_app, app['cmd'])
            hbox.pack_end(btn, False, False, 5)
            
            # Add the horizontal box to the list box
            self.list_box.add(hbox)
        
        # Show all widgets
        self.list_box.show_all()
    
    def on_search_changed(self, entry):
        """
        Handle search input change.
        """
        self.current_search = entry.get_text()
        self.refresh_display()
    
    def on_launch_app(self, button, command):
        """
        Handle application launch when a launch button is clicked.
        
        Args:
            button (Gtk.Button): The launch button that was clicked
            command (str): The command to execute
        """
        # Run the application in a separate thread to avoid blocking the GUI
        thread = threading.Thread(target=self.launcher_logic.launch_with_validation, args=(command,))
        thread.start()
    
    def on_regenerate_clicked(self, button):
        """
        Handle the Regenerate button click to import .desktop files.
        """
        # Get all system applications
        system_apps = self.desktop_parser.scan_applications()
        
        # Add them to the config (for now, adding to Uncategorized category)
        for app in system_apps:
            # Check if app already exists in config to avoid duplicates
            exists = False
            for category_apps in self.config_manager.config['categories'].values():
                for existing_app in category_apps:
                    if existing_app['name'] == app['name'] and existing_app['cmd'] == app['cmd']:
                        exists = True
                        break
                if exists:
                    break
            
            # Only add if it doesn't already exist
            if not exists:
                self.config_manager.add_application_to_category("System Apps", app)
        
        # Refresh the display
        self.refresh_display()
    
    def on_edit_config_clicked(self, button):
        """
        Handle the Edit Config button click to open config in external editor.
        """
        config_path = self.config_manager.config_path
        
        try:
            # Try to open with the default editor
            editor = 'xdg-open'  # Use xdg-open to open with default application
            subprocess.Popen([editor, str(config_path)])
        except Exception as e:
            logging.error(f"Error opening config file: {e}")
            # If xdg-open fails, try using the EDITOR environment variable
            try:
                editor = subprocess.check_output(['bash', '-c', 'echo $EDITOR']).decode().strip()
                if editor:
                    subprocess.Popen([editor, str(config_path)])
                else:
                    logging.error("No default editor found")
            except Exception as e2:
                logging.error(f"Error opening config file with $EDITOR: {e2}")
    
    def on_quit_clicked(self, button):
        """
        Handle the Quit button click.
        """
        self.window.hide()
    
    def show(self):
        """
        Show the main window.
        """
        self.window.present()
    
    def hide(self):
        """
        Hide the main window.
        """
        self.window.hide()
    
    def toggle_visibility(self):
        """
        Toggle the visibility of the main window.
        """
        if self.window.get_property('is-active'):
            self.hide()
        else:
            self.show()