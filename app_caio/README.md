
# PCB Serial Controller (Python + PySide6)

Um aplicativo simples (tema escuro) para enviar e receber mensagens de/para uma placa via **STLink (porta COM virtual)**.

## Recursos
- Seleção de porta COM (com botão **Atualizar**).
- Seleção de **baud** e formato **8N1/8E1/8O1/7E1/8N2**.
- **Conectar/Desconectar**.
- **Comandos Rápidos**: 
  - *Página →* envia `p plus` (+ terminador configurado)
  - *Página ←* envia `p minus` (+ terminador configurado)
- Envio **manual** de mensagens com escolha de **terminador**: `LF`, `CR`, `CRLF` ou **Nenhum**.
- Área de **log** (somente leitura) com timestamps, indicando `>>` (enviado) e `<<` (recebido).

## Pré-requisitos
- Python 3.9+
- Windows, Linux ou macOS.
- Um **STLink** que exponha porta serial virtual (VCP).

## Instalação
```bash
# (opcional) criar venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

## Execução
```bash
python app.py
```

## Dicas/Notas
- Por padrão o baud é **115200** e formato **8N1** — ajuste conforme seu firmware.
- O app tenta **pré-selecionar automaticamente** a porta que contenha "STLink"/"STMicro" na descrição.
- Os botões **Página →** / **Página ←** enviam `p plus` e `p minus` respectivamente, adicionando o terminador escolhido.
- Se seu firmware **não usa terminador**, altere para **"Nenhum"** no seletor de terminador.
- Caso precise de pares de controle de fluxo (RTS/CTS, DSR/DTR), o código está pronto para ajustar (ver `SerialThread`).

## Estrutura
```
pcb_serial_controller/
├─ app.py
├─ requirements.txt
└─ README.md
```

## Licença
Livre uso para fins pessoais e acadêmicos.
