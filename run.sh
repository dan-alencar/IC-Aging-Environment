#!/bin/bash
# Root launcher — reuses App_Nexys/.venv for PySide6, then runs launcher.py.
# Each sub-app manages its own .venv independently when spawned.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NEXYS_DIR="$SCRIPT_DIR/App_Nexys"

# --- 1. Ensure App_Nexys venv exists (it provides PySide6 for the launcher) ---
if [ ! -f "$NEXYS_DIR/.venv/bin/activate" ]; then
    echo "App_Nexys venv not found. Creating..."
    python3 -m venv "$NEXYS_DIR/.venv"
    "$NEXYS_DIR/.venv/bin/python" -m pip install --upgrade pip
    "$NEXYS_DIR/.venv/bin/python" -m pip install -r "$NEXYS_DIR/requirements.txt"
fi

# --- 2. Activate venv ---
source "$NEXYS_DIR/.venv/bin/activate"

# --- 3. Fix Qt library path (Linux Mint / system Qt conflict) ---
PYSIDE_LIB_PATH=$(find "$NEXYS_DIR/.venv" -name "libQt6Core.so.6" -exec dirname {} \; 2>/dev/null | head -1)

if [ -z "$PYSIDE_LIB_PATH" ]; then
    echo "ERROR: PySide6 libraries not found in App_Nexys/.venv."
    echo "Delete App_Nexys/.venv and re-run to reinstall."
    exit 1
fi

export LD_LIBRARY_PATH="$PYSIDE_LIB_PATH:$LD_LIBRARY_PATH"
export QT_PLUGIN_PATH=""
export QML2_IMPORT_PATH=""

# --- 4. Launch the selector dialog ---
echo "Starting IC Aging Environment launcher..."
cd "$SCRIPT_DIR"
python launcher.py

deactivate
