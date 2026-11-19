#!/usr/bin/env bash
# Suite de simulacao (Icarus Verilog >= 11). Nao precisa de Quartus.
#   bash scripts/run_sim.sh          # roda tudo
# Usa MODELOS COMPORTAMENTAIS (sim/models): nao e o modelo oficial da Intel nem
# timing de silicio. Serve para provar a logica do laco, as flags e a telemetria.
set -uo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/src"
command -v iverilog >/dev/null || { echo "iverilog nao encontrado (Ubuntu/WSL: sudo apt install iverilog)"; exit 2; }
out="$(mktemp -d)"; fail=0
RTL="rtl/top/max10_aging_top.sv rtl/aging_sensor/aging_sensor_core.sv rtl/aging_sensor/critical_path_chain.sv rtl/aging_sensor/scc_controller.sv rtl/uart/uart_tx.sv rtl/uart/uart_packet_sender.sv rtl/display/hex7seg.sv"
MODELS="sim/models/fiftyfivenm_lcell_comb_model.sv sim/models/aging_pll_model.sv"

run() { # nome, comando de compilacao..., (plusargs depois de --)
  local name="$1"; shift
  local plus=(); local comp=()
  while [ $# -gt 0 ]; do [ "$1" = "--" ] && { shift; plus=("$@"); break; }; comp+=("$1"); shift; done
  if iverilog -g2012 "${comp[@]}" -o "$out/$name.vvp" 2>"$out/$name.err" && \
     vvp "$out/$name.vvp" "${plus[@]}" | tee "$out/$name.log" | grep -q "^PASS"; then
    echo "[ OK ] $name"
  else
    echo "[FAIL] $name  (log: $out/$name.log)"; fail=1
  fi
}

# 1) controlador isolado, laco fechado (catcher 2,5 ns): medidas, rastreio, saturacao, timeout, lock, Tabela 7
run scc_loop_c2500 sim/scc_loop_tb.sv rtl/aging_sensor/scc_controller.sv
# 2) mesmo teste com o catcher ANTIGO (10 ns): reproduz o 1065 da Tabela 7 e o detector marca saturacao
run scc_table7_c10000 -P scc_loop_tb.C_PS=10000 -P scc_loop_tb.TABLE7_ONLY=1 sim/scc_loop_tb.sv rtl/aging_sensor/scc_controller.sv
# 3) topo completo + pacote UART, varios atrasos de cadeia (d = 50 x STAGE_DELAY_PS)
top() { # delay_ps_por_estagio catcher_ps k_esperado sat_esperado
  run "top_d$(( $1 * 50 ))_c$2" -DSTAGE_DELAY_PS=$1 -DCATCHER_PS=$2 $MODELS sim/max10_top_tb.sv $RTL -- +EXPECT_K=$3 +EXPECT_SAT=$4
}
top 584 2500 957 0     # d = 29,2 ns (corner lento)
top 348 2500 1023 0    # d = 17,4 ns (ambiente, medido em placa)
top 120 2500 1087 0    # d =  6,0 ns (antes: saturava em 1065)
top 120 10000 1065 1   # catcher antigo: satura e agora e MARCADO
[ $fail -eq 0 ] && echo "TODOS OS TESTES PASSARAM" || echo "HOUVE FALHAS"
exit $fail
