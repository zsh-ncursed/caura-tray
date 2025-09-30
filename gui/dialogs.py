import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import logging

class ImportDialog:
    """
    Dialog for importing applications from .desktop files with category selection.
    """
    
    def __init__(self, parent_window, applications):
        """
        Initialize the import dialog.
        
        Args:
            parent_window (Gtk.Window): Parent window for the dialog
            applications (list): List of applications to import
        """
        self.parent_window = parent_window
        self.applications = applications
        self.selected_apps = []
        
        # Create dialog window
        self.dialog = Gtk.Dialog(
            title="Import Applications",
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
        )
        
        self.dialog.set_default_size(500, 400)
        
        # Create content area
        content_area = self.dialog.get_content_area()
        
        # Create label
        label = Gtk.Label(label="Select applications to import and choose categories:")
        label.set_margin_bottom(10)
        content_area.pack_start(label, False, False, 0)
        
        # Create scrolled window for the list of applications
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        content_area.pack_start(scrolled_window, True, True, 0)
        
        # Create list box for applications
        self.app_list_box = Gtk.ListBox()
        self.app_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window.add(self.app_list_box)
        
        # Add applications to the list
        for app in applications:
            self.add_app_to_list(app)
        
        # Show all widgets
        self.dialog.show_all()
    
    def add_app_to_list(self, app):
        """
        Add an application to the list with checkbox and category selection.
        
        Args:
            app (dict): Application information with 'name', 'cmd', etc.
        """
        # Create a horizontal box for each app
        hbox = Gtk.HBox(spacing=10)
        hbox.set_margin_left(5)
        hbox.set_margin_right(5)
        hbox.set_margin_top(5)
        hbox.set_margin_bottom(5)
        
        # Checkbox to select/deselect the app
        checkbox = Gtk.CheckButton()
        checkbox.set_active(True)  # Select by default
        hbox.pack_start(checkbox, False, False, 0)
        
        # App name label
        name_label = Gtk.Label(label=app['name'])
        name_label.set_xalign(0)
        hbox.pack_start(name_label, True, True, 0)
        
        # Category selection combo box
        category_combo = Gtk.ComboBoxText()
        category_combo.append_text("Uncategorized")
        category_combo.append_text("System Apps")
        category_combo.append_text("Office")
        category_combo.append_text("Development")
        category_combo.append_text("Graphics")
        category_combo.append_text("Audio")
        category_combo.append_text("Video")
        category_combo.append_text("Games")
        category_combo.append_text("Internet")
        category_combo.set_active(0)  # Default to Uncategorized
        hbox.pack_end(category_combo, False, False, 0)
        
        # Store app info with the checkbox and combo box
        checkbox.app_info = app
        checkbox.category_combo = category_combo
        
        # Add to the list box
        self.app_list_box.add(hbox)
    
    def run(self):
        """
        Run the dialog and return the selected applications with categories.
        
        Returns:
            list: List of tuples (app_info, category_name) for selected applications
        """
        response = self.dialog.run()
        
        selected_apps = []
        if response == Gtk.ResponseType.OK:
            # Get all children from the list box
            for child in self.app_list_box.get_children():
                # Get the checkbox (first child of the hbox)
                checkbox = child.get_children()[0]
                
                if checkbox.get_active():  # If selected
                    app_info = checkbox.app_info
                    category_combo = checkbox.category_combo
                    category = category_combo.get_active_text()
                    
                    selected_apps.append((app_info, category))
        
        self.dialog.destroy()
        return selected_apps


class ErrorDialog:
    """
    Simple dialog to show error messages to the user.
    """
    
    @staticmethod
    def show(parent_window, message, title="Error"):
        """
        Show an error dialog with the specified message.
        
        Args:
            parent_window (Gtk.Window): Parent window for the dialog
            message (str): Error message to display
            title (str): Title of the dialog
        """
        dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()


class ConfirmationDialog:
    """
    Dialog to confirm potentially destructive actions.
    """
    
    @staticmethod
    def show(parent_window, message, title="Confirm Action"):
        """
        Show a confirmation dialog.
        
        Args:
            parent_window (Gtk.Window): Parent window for the dialog
            message (str): Confirmation message to display
            title (str): Title of the dialog
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=message
        )
        dialog.set_title(title)
        response = dialog.run()
        dialog.destroy()
        
        return response == Gtk.ResponseType.YES


class ProgressDialog:
    """
    Dialog to show progress for long-running operations.
    """
    
    def __init__(self, parent_window, title="Progress"):
        """
        Initialize the progress dialog.
        
        Args:
            parent_window (Gtk.Window): Parent window for the dialog
            title (str): Title of the dialog
        """
        self.dialog = Gtk.Dialog(
            title=title,
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL
        )
        
        # Create content area
        content_area = self.dialog.get_content_area()
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        content_area.pack_start(self.progress_bar, True, True, 0)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel)
        content_area.pack_start(cancel_button, False, False, 0)
        
        # Initial state
        self.cancelled = False
        
        self.dialog.show_all()
    
    def set_fraction(self, fraction):
        """
        Set the progress fraction (0.0 to 1.0).
        
        Args:
            fraction (float): Progress fraction
        """
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{int(fraction * 100)}%")
    
    def set_text(self, text):
        """
        Set the progress text.
        
        Args:
            text (str): Progress text
        """
        self.progress_bar.set_text(text)
    
    def on_cancel(self, button):
        """
        Handle cancel button click.
        """
        self.cancelled = True
    
    def is_cancelled(self):
        """
        Check if the operation was cancelled.
        
        Returns:
            bool: True if cancelled, False otherwise
        """
        return self.cancelled
    
    def close(self):
        """
        Close the dialog.
        """
        self.dialog.destroy()