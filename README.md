# Caura Tray - System Application Launcher

Caura Tray is a desktop launcher for Linux that resides in the system tray. It provides a categorized application menu with dropdown lists, search functionality, import from .desktop files, and configuration management.

## Features

- System tray icon with context menu
- Application categories: General, Development, Games, Graphics, Multimedia, Internet, Office, Settings, System
- Icons for categories and applications
- Dropdown menu with applications by category
- Quick launch applications (Terminal, Web Browser, File Manager, Mail Client, Messenger) at the top of the menu
- Icon visibility settings
- Show/hide quick launch applications setting
- Customizable quick launch commands
- Regenerate function for importing .desktop files
- Safe application launching
- DBus integration

## Installation

### On Arch Linux

1. Make sure you have the required dependencies installed:
   ```bash
   sudo pacman -S python python-gobject python-dbus python-pillow libappindicator-gtk3
   ```

2. Copy the source code to a directory

3. Install Python dependencies:
   ```bash
   pip install pycairo PyGObject
   ```

## Usage

1. Run the application:
   ```bash
   ./run_launcher.sh
   ```

2. The application will create an icon in the system tray

3. Click the icon to open the menu with application categories

4. Click "Regenerate" to update the application list

5. Click "Settings" to configure icon visibility

## Settings

- **Show icons in menu**: Enable/Disable icon display in menu
- Settings are saved in `~/.local/share/tray_launcher/config.json`

## Project Structure

```
caura-tray/
├── launcher.py              # Entry point, main application
├── run_launcher.sh          # Script to launch the application
├── RUNNING.md               # Launch instructions
├── import_apps.py           # Script for importing .desktop files
├── install.sh               # Dependencies installation script
├── PKGBUILD                 # Arch Linux package build file
├── dbus_integration.py      # DBus integration
├── launcher_logic.py        # Application launching logic
├── tray-launcher.desktop    # Desktop environment launch file
├── gui/
│   ├── main_window.py       # Main window
│   ├── settings_dialog.py   # Settings dialog
│   └── dialogs.py           # Additional dialogs
├── tray/
│   └── gtk_tray_icon.py     # GTK tray icon implementation
├── storage/
│   └── config_manager.py    # Configuration management
├── parser/
│   └── desktop_parser.py    # .desktop file parser
└── tests/
    └── test_components.py   # Unit tests
```

## Requirements

- Python 3.8+
- GTK 3
- PyGObject
- python-dbus
- python-pillow
- libappindicator-gtk3
- pycairo

## Application Categories

Applications are automatically mapped to one of the following categories:

- General: Utilities, archivers, calculators, etc.
- Development: IDEs, code editors, debuggers, etc.
- Games: All gaming applications
- Graphics: Image editors, drawing applications, etc.
- Multimedia: Audio/video players, recorders, etc.
- Internet: Browsers, email clients, chat applications, etc.
- Office: Document editors, spreadsheets, etc.
- Settings: Control panels and system configuration
- System: System utilities and tools

## Configuration Files

- Settings and application list: `~/.local/share/tray_launcher/config.json`
- Application log: `~/.local/share/tray_launcher/tray_launcher.log`

## Development

For development and testing:

1. Clone the repository
2. Install dependencies
3. Run `./run_launcher.sh`
4. Check functionality
5. Run tests (if available): `python -m unittest discover tests/`

## License

MIT License