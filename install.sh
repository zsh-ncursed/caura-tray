#!/bin/bash

# Caura Tray installation script for Arch Linux

echo "Installing Caura Tray..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root" 
   exit 1
fi

# Install dependencies
echo "Installing dependencies..."
sudo pacman -S --needed python python-gobject python-dbus python-pillow libappindicator-gtk3

# Install Python dependencies
if command -v pip &> /dev/null; then
    echo "Installing Python dependencies..."
    pip install --user pycairo PyGObject
else
    echo "pip is not installed. Please install pip first."
    exit 1
fi

echo "Caura Tray dependencies installed successfully."
echo "You can now run the application with: ./run_launcher.sh"