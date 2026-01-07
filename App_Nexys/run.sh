#!/bin/bash

# --- 1. Ativa o ambiente virtual (.venv) ---
echo "Ativando o ambiente virtual..."
source .venv/bin/activate

# --- 2. Localiza o diretório das bibliotecas do PySide6 ---
# Busca pelo arquivo libQt6Core.so.6 dentro do venv
PYSIDE_LIB_PATH=$(find .venv -name "libQt6Core.so.6" -exec dirname {} \;)

if [ -z "$PYSIDE_LIB_PATH" ]; then
    echo "ERRO: Não foi possível encontrar a pasta das bibliotecas PySide6 no .venv."
    echo "Certifique-se de que o PySide6 foi instalado corretamente."
    exit 1
fi

# --- 3. Exporta LD_LIBRARY_PATH para forçar o uso das libs do venv ---
# Isso resolve o conflito de versão com as bibliotecas Qt do sistema Linux Mint
export LD_LIBRARY_PATH="$PYSIDE_LIB_PATH:$LD_LIBRARY_PATH"

# --- 4. Remove caminhos de plugins do sistema para evitar conflitos de carregamento ---
export QT_PLUGIN_PATH=""
export QML2_IMPORT_PATH=""

# --- 5. Executa a aplicação principal ---
echo "Iniciando a aplicação..."
python App.py

# --- 6. Desativa o ambiente virtual ao final (opcional, mas bom costume) ---
# Note: Esta linha só é executada se você rodar o script usando ./run.sh
deactivate
