#!/bin/bash
# Linux Launcher for Android Forensics Tool GUI

echo "Starting Android Forensics Tool (Linux)..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  Fedora: sudo dnf install python3"
    echo "  Arch: sudo pacman -S python"
    exit 1
fi

# Check Python version
python3 --version

# Run the Linux GUI
python3 gui_linux.py

if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred. Please check the error message above."
    read -p "Press Enter to exit..."
fi

