#!/usr/bin/env bash
# Grava o firmware B (ou volta ao antigo) no STM32 de UMA placa, escolhendo o ST-Link pelo
# UID do STM32, e não pelo serial: com a Nucleo no USB, o STM32_Programmer_CLI mostra um
# dos STLINK-V3 com o serial dela (em 04/11/2026, o da placa A aparecia como 066CFF…).
#
#   ./gravar.sh A            # firmware B na placa A
#   ./gravar.sh B            # firmware B na placa B
#   ./gravar.sh C            # firmware B na placa C (a 3ª placa, ligada em 11/11/2026)
#   ./gravar.sh A antigo     # volta a placa A ao firmware de antes (../fw_TEL_125k_84KB.bin)
#   ./gravar.sh listar       # só mostra qual ST-Link chega em qual STM32 (não grava nada)
#
# Feche o D&T Monitor antes. O script lê o UID atrás de cada ST-Link (sem reset) e só apaga e
# grava no que tiver o UID da placa pedida. Na primeira gravação de cada STM32, copia antes a
# flash inteira para ../placa<X>_UID<...>_antes_<data>.bin (só leitura). Depois confere a
# gravação (-v), reinicia o STM32 e lê o UID de novo.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI=${CLI:-/opt/st/stm32cubeide_1.19.0/plugins/com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.linux64_2.2.200.202503041107/tools/bin/STM32_Programmer_CLI}

case "${1:-}" in
  A) want="0028001A 30325015 20343046" ;;
  B) want="002E002C 30325014 20343046" ;;
  C) want="000F0029 32325009 20363646" ;;
  listar) want="(só listar)" ;;
  *) sed -n '2,16p' "$0"; exit 2 ;;
esac
if [[ "${2:-}" == antigo ]]; then
  bin="$here/../fw_TEL_125k_84KB.bin"; md5_ok=cda19662012767166e375207f6a1e8c6
else
  bin="$here/bin/fw_hub_v6_20261106.bin"; md5_ok=2719cf22ea77c8fc3aaca2c9df02de69
fi
[[ "$(md5sum "$bin" | cut -d' ' -f1)" == "$md5_ok" ]] || { echo "md5 errado em $bin"; exit 1; }

if pgrep -f "10_DT_Monitor/App.py" >/dev/null; then
  echo "Feche o D&T Monitor antes (ele está com a porta do ST-Link aberta)."; exit 1
fi

strip() { sed 's/\x1b\[[0-9;]*m//g'; }
mapfile -t sns < <("$CLI" -l st 2>&1 | strip | awk '/ST-LINK SN *:/ {print $NF}' | sort -u)
target=""
for sn in "${sns[@]}"; do
  uid=$("$CLI" -c port=SWD sn="$sn" mode=HOTPLUG -r32 0x1FFF7590 0xC 2>&1 | strip \
        | awk -F' : ' '/^0x1FFF7590 :/ {print $2}' | xargs || true)
  echo "ST-Link $sn → STM32 UID ${uid:-?}"
  [[ "$uid" == "$want" ]] && target="$sn"
done
[[ "$1" == listar ]] && exit 0
[[ -n "$target" ]] || { echo "Nenhum ST-Link chega ao STM32 da placa $1 (UID $want). Nada foi gravado."; exit 1; }

# Cópia da flash de antes, se este STM32 ainda não tem nenhuma em ../ (A e B já têm).
uid0=${want%% *}
if ! compgen -G "$here/../*UID${uid0}*.bin" >/dev/null; then
  backup="$here/../placa$1_UID${uid0}_antes_$(date +%Y%m%d_%H%M).bin"
  echo
  echo "Copiando a flash atual (2 MB, só leitura) para $(basename "$backup")..."
  bout=$("$CLI" -c port=SWD sn="$target" mode=HOTPLUG -r32 0x1FFF7590 0xC \
         -u 0x08000000 0x200000 "$backup" 2>&1 | strip || true)
  bgot=$(echo "$bout" | awk -F' : ' '/^0x1FFF7590 :/ {print $2; exit}' | xargs)
  if [[ "$bgot" != "$want" || ! -f "$backup" || "$(stat -c %s "$backup" 2>/dev/null)" != 2097152 ]]; then
    echo "$bout" | tail -5
    echo "!!! A cópia da flash não deu certo (UID lido: ${bgot:-?}). Nada foi apagado."; exit 1
  fi
  echo "Cópia ok, md5 $(md5sum "$backup" | cut -d' ' -f1)"
fi

echo
echo "Gravando $(basename "$bin") na placa $1 pelo ST-Link listado como $target (apaga a flash inteira)..."
out=$("$CLI" -c port=SWD sn="$target" -r32 0x1FFF7590 0xC -e all -w "$bin" 0x08000000 -v -rst 2>&1 | strip)
echo "$out" | grep -E "^0x1FFF7590 :|Mass erase|Download verified|File download complete|Error" || true
got=$(echo "$out" | awk -F' : ' '/^0x1FFF7590 :/ {print $2; exit}' | xargs)
[[ "$got" == "$want" ]] || echo "!!! ATENÇÃO: o UID lido na gravação ($got) não é o da placa $1."
echo "$out" | grep -q "Download verified successfully" && echo "OK: gravado e conferido." \
  || { echo "!!! A conferência da gravação não passou. Veja a saída completa acima."; exit 1; }
