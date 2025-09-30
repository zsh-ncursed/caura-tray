# Running Caura Tray

## Quick Start

To run the Caura Tray application, you have several options:

### Option 1: Using the launcher script (Recommended)
```bash
./run_launcher.sh
```

### Option 2: Direct Python execution
```bash
python launcher.py
```

### Option 3: Using the desktop file
The `tray-launcher.desktop` file can be used to launch the application from your desktop environment.

## Prerequisites

Make sure you have the required dependencies installed:

### Arch Linux
```bash
sudo pacman -S python python-gobject python-dbus python-pillow libappindicator-gtk3
pip install pycairo PyGObject
```

### Manual installation
For manual installation, you can run the provided installation script:
```bash
./install.sh
```

## Features

Once running, Caura Tray provides:

- System tray icon with context menu
- Categorized application launcher with icons
- Categories: General, Development, Games, Graphics, Multimedia, Internet, Office, Settings, System
- Each application in a single category with appropriate icon
- Settings dialog to toggle icon visibility
- Regenerate function to import new .desktop files
- JSON-based configuration management
- DBus integration for system events

## Configuration

The configuration file is stored at `~/.local/share/tray_launcher/config.json`

## Usage Instructions

1. After starting the application, you'll see an icon in the system tray
2. Click the icon to open the menu with application categories
3. Hover over a category to see its applications
4. Click an application to launch it
5. Use "Regenerate" to scan and import new .desktop files
6. Use "Settings" to toggle icon visibility on/off

## Troubleshooting

If you encounter issues:
1. Make sure all dependencies are installed
2. Verify that the script is being run from the correct directory
3. Check that your system has a running X session for the GUI components
4. If icons don't appear, check if the icon theme is properly configured
5. Check `~/.local/share/tray_launcher/tray_launcher.log` for error messages