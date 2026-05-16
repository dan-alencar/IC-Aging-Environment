#!/bin/bash
# App_2Nexys standalone launcher — same pattern as App_Nexys/run.sh.
set -e

cd "$(dirname "$0")"

# --- 1. Ensure venv exists ---
if [ ! -f ".venv/bin/activate" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

# --- 2. Activate venv ---
echo "Activating virtual environment..."
source .venv/bin/activate

# --- 3. Fix Qt library path (Linux Mint / system Qt conflict) ---
PYSIDE_LIB_PATH=$(find .venv -name "libQt6Core.so.6" -exec dirname {} \; 2>/dev/null | head -1)

if [ -z "$PYSIDE_LIB_PATH" ]; then
    echo "ERROR: PySide6 libraries not found in .venv."
    echo "Delete .venv and re-run to reinstall."
    exit 1
fi

export LD_LIBRARY_PATH="$PYSIDE_LIB_PATH:$LD_LIBRARY_PATH"
export QT_PLUGIN_PATH=""
export QML2_IMPORT_PATH=""

# --- 4. Launch app ---
echo "Starting App_2Nexys..."
python App.py

deactivate
