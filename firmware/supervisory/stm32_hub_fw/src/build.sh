#!/usr/bin/env bash
# Compila o firmware da arquitetura B sem abrir o STM32CubeIDE (mesmos flags do .cproject, Debug).
#   ./build.sh            → out/Teste_Aging.bin
#   ./build.sh test       → também roda os testes do enlace FPGA no PC (tests_host)
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
build="$(date +%Y%m%d)"
rm -rf "$here/out"      # sempre do zero: o binário não pode depender do que sobrou de outro build
make -C "$here" -f Makefile.cubeide PROJ=Latchup_FW_hub OUT=out \
     EXTRA="-DHUB_FW_BUILD=\\\"$build\\\"" -j"$(nproc)"
md5sum "$here/out/Teste_Aging.bin"
if [[ ${1:-} == test ]]; then
  (cd "$here/Latchup_FW_hub" && python3 tests_host/test_fl_host.py)
fi
