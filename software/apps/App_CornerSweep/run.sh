#!/bin/bash
set -e

cd "$(dirname "$0")"

# Reuse App_Nexys venv (shares PySide6 and pyserial)
VENV="../App_Nexys/.venv"

if [ ! -f "$VENV/bin/activate" ]; then
    echo "Ambiente virtual não encontrado em $VENV."
    echo "Criando venv local..."
    python3 -m venv .venv
    VENV=".venv"
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -r requirements.txt
fi

source "$VENV/bin/activate"

# Resolve Qt lib path to avoid conflicts with system Qt on Linux Mint
PYSIDE_LIB=$(find "$VENV" -name "libQt6Core.so.6" -exec dirname {} \; 2>/dev/null | head -1)
if [ -z "$PYSIDE_LIB" ]; then
    echo "ERRO: libQt6Core.so.6 não encontrada no venv."
    exit 1
fi

export LD_LIBRARY_PATH="$PYSIDE_LIB:$LD_LIBRARY_PATH"
export QT_PLUGIN_PATH=""
export QML2_IMPORT_PATH=""

echo "Iniciando App_CornerSweep..."
python App.py
