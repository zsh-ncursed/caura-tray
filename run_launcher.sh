#!/bin/bash

# Tray Launcher - A desktop launcher application for Linux with system tray integration
# Launcher script for easy execution

# Exit on any error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Tray Launcher - Desktop Application Launcher"
echo "============================================="
echo "Current directory: $SCRIPT_DIR"
echo "Python executable: $(which python)"
echo

# Check if required dependencies are available
echo "Checking for required dependencies..."

# Check for Python modules
MISSING_DEPS=()
REQUIRED_MODULES=("gi" "pystray" "dbus" "PIL")

for module in "${REQUIRED_MODULES[@]}"; do
    if ! python -c "import $module" 2>/dev/null; then
        MISSING_DEPS+=("$module")
    fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "Error: Missing required Python modules: ${MISSING_DEPS[*]}"
    echo
    echo "Please install them using your package manager:"
    echo "  Arch Linux: sudo pacman -S python-gobject python-dbus python-pillow python-pystray"
    echo "  Debian/Ubuntu: sudo apt-get install python3-gi python3-dbus gir1.2-gtk-3.0 python3-pil python3-pystray"
    echo
    exit 1
fi

echo "All required dependencies are available."
echo

# Function to handle exit
cleanup() {
    echo
    echo "Tray Launcher is shutting down..."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Launching Tray Launcher..."
echo "The application will appear in your system tray."
echo "Press Ctrl+C to quit the application."
echo

# Execute the main Python script
if python launcher.py; then
    echo
    echo "Tray Launcher has stopped normally."
else
    echo
    echo "Tray Launcher stopped with an error."
    exit 1
fi