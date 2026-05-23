"""
Corner-sweep test state machine.

Phases
──────
IDLE            → test not started
WAITING_TEMP    → polling until DUT reaches target temperature for TEMP_STABLE_TICKS
CORNER_SETTLING → PSU set to corner voltage; waiting for VCCINT to settle
CORNER_SAMPLING → collecting SAMPLES_PER_CORNER readings; recording slack + errors
SWEEP_SETTLING  → PSU stepped down by SWEEP_STEP_V; waiting for VCCINT to settle
SWEEP_SAMPLING  → collecting SWEEP_SAMPLE_TICKS readings; checking for adder errors
DONE            → test finished; logger closed
"""
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from PySide6.QtCore import QObject, QTimer, Signal, Slot

import config
from logger import CornerSweepLogger


class Phase(str, Enum):
    IDLE            = "Aguardando início"
    WAITING_TEMP    = "Estabilizando temperatura"
    CORNER_SETTLING = "Aguardando tensão — corner"
    CORNER_SAMPLING = "Medindo corner"
    SWEEP_SETTLING  = "Aguardando tensão — sweep"
    SWEEP_SAMPLING  = "Varredura de falha"
    DONE            = "Concluído"


@dataclass
class CornerResult:
    voltage_cmd:  float
    vccint_list:  List[float] = field(default_factory=list)
    slack_list:   List[int]   = field(default_factory=list)
    fail_any:     bool = False
    wrong_total:  int  = 0
    errcnt_total: int  = 0

    @property
    def vccint_mean(self) -> float:
        return sum(self.vccint_list) / max(len(self.vccint_list), 1)

    @property
    def slack_mean(self) -> float:
        return sum(self.slack_list) / max(len(self.slack_list), 1) if self.slack_list else 0.0

    @property
    def slack_min(self) -> int:
        return min(self.slack_list) if self.slack_list else 0

    @property
    def slack_max(self) -> int:
        return max(self.slack_list) if self.slack_list else 0


class CornerSweepSequencer(QObject):
    log_message   = Signal(str)
    phase_changed = Signal(str)           # Phase.value string
    status_update = Signal(dict)          # live readings every tick
    corner_done   = Signal(int, object)   # (corner_index, CornerResult)
    sweep_tick    = Signal(float, int, bool)  # (v_cmd, slack, error_detected)
    test_finished = Signal(bool, str)     # (had_failure, summary_message)

    def __init__(self, arduino, psu, dut):
        super().__init__()
        self._arduino = arduino
        self._psu     = psu
        self._dut     = dut

        self._phase:          Phase = Phase.IDLE
        self._logger:         Optional[CornerSweepLogger] = None
        self._start_time:     float = 0.0
        self._settings:       dict  = {}

        # Counters reset at each phase transition
        self._stable_ticks:       int = 0
        self._settle_ticks:       int = 0
        self._settle_timeout:     int = 0
        self._sample_ticks:       int = 0
        self._sweep_sample_ticks: int = 0

        # Corner tracking
        self._corner_idx:     int = 0
        self._corner_results: List[CornerResult] = []
        self._current_result: Optional[CornerResult] = None

        # Sweep tracking
        self._sweep_v:      float = 0.0
        self._failure_volt: Optional[float] = None

        self._timer = QTimer(self)
        self._timer.setInterval(config.LOG_INTERVAL_MS)
        self._timer.timeout.connect(self._tick)

    # ── Public API ────────────────────────────────────────────────────────────

    @Slot(dict)
    def start_test(self, settings: dict):
        if self._phase != Phase.IDLE:
            self.log_message.emit("ERRO: teste já em execução.")
            return

        self._settings       = settings
        self._start_time     = time.time()
        self._stable_ticks   = 0
        self._corner_idx     = 0
        self._corner_results = []
        self._current_result = None
        self._failure_volt   = None

        target_temp = settings.get('target_dut_temp', 85.0)

        self._logger = CornerSweepLogger(
            config.LOG_FOLDER,
            settings.get('test_name', 'sweep'),
            target_temp,
            config.CORNERS_V,
            config.SWEEP_STEP_V,
        )
        self.log_message.emit(f"Log: {self._logger.filepath}")

        if config.ARDUINO_ENABLED and self._arduino.is_ready:
            oven_sp = settings.get('oven_setpoint', 100.0)
            self._arduino.set_target_setpoint(oven_sp)
            self._arduino.start_test_oven()
            self.log_message.emit(f"Forno: setpoint → {oven_sp:.1f}°C")

        if config.PSU_ENABLED and self._psu.is_running:
            self._psu.turn_on()

        self._set_phase(Phase.WAITING_TEMP)
        self._timer.start()
        self.log_message.emit(
            f"Aguardando DUT atingir {target_temp:.1f}°C "
            f"(±{config.TEMP_STABLE_TOL_C}°C por {config.TEMP_STABLE_TICKS} s)"
        )

    @Slot()
    def stop_test(self):
        if self._phase == Phase.IDLE:
            return
        self.log_message.emit("Teste interrompido pelo operador.")
        self._shutdown(had_failure=False, msg="Interrompido pelo operador.")

    # ── Timer callback ────────────────────────────────────────────────────────

    def _tick(self):
        t_oven, _sp, _out                           = self._arduino.get_latest_data()
        v_psu, c_psu                                = self._psu.get_latest_data()
        t_dut, s_dut, v_dut, fail, wrong, corr, err = self._dut.get_latest_data()
        elapsed = time.time() - self._start_time

        data = {
            'timestamp':      datetime.now().strftime('%H:%M:%S'),
            'elapsed_s':      f"{elapsed:.1f}",
            'dut_temp_c':     t_dut,
            'oven_temp_c':    t_oven,
            'dut_volt_v':     v_dut,
            'psu_volt_v':     v_psu,
            'psu_curr_a':     c_psu,
            'dut_slack':      s_dut,
            'dut_fail':       fail,
            'dut_wrong':      wrong,
            'dut_correct':    corr,
            'dut_error_count': err,
        }
        self.status_update.emit(data)

        # Safety guards (applies to all active phases)
        if t_dut > config.MAX_DUT_TEMP_C and t_dut > 0:
            self.log_message.emit(
                f"SEGURANÇA: Temp DUT {t_dut:.1f}°C > {config.MAX_DUT_TEMP_C}°C"
            )
            self._shutdown(had_failure=False, msg="Parada de segurança — temperatura DUT.")
            return
        if c_psu > config.MAX_PSU_CURRENT_A and c_psu > 0:
            self.log_message.emit(
                f"SEGURANÇA: Corrente PSU {c_psu:.3f}A > {config.MAX_PSU_CURRENT_A}A"
            )
            self._shutdown(had_failure=False, msg="Parada de segurança — sobrecorrente.")
            return

        if   self._phase == Phase.WAITING_TEMP:
            self._do_waiting_temp(t_dut)
        elif self._phase == Phase.CORNER_SETTLING:
            self._do_corner_settling(v_dut)
        elif self._phase == Phase.CORNER_SAMPLING:
            self._do_corner_sampling(v_dut, s_dut, fail, wrong, err, elapsed, data)
        elif self._phase == Phase.SWEEP_SETTLING:
            self._do_sweep_settling(v_dut)
        elif self._phase == Phase.SWEEP_SAMPLING:
            self._do_sweep_sampling(v_dut, s_dut, fail, wrong, err, elapsed, data)

    # ── State handlers ────────────────────────────────────────────────────────

    def _do_waiting_temp(self, t_dut: float):
        target = self._settings.get('target_dut_temp', 85.0)
        if abs(t_dut - target) <= config.TEMP_STABLE_TOL_C and t_dut > 0:
            self._stable_ticks += 1
        else:
            self._stable_ticks = 0

        # Log progress every 10 ticks
        if self._stable_ticks > 0 and self._stable_ticks % 10 == 0:
            self.log_message.emit(
                f"Temp DUT {t_dut:.1f}°C  estável {self._stable_ticks}/{config.TEMP_STABLE_TICKS} s"
            )

        if self._stable_ticks >= config.TEMP_STABLE_TICKS:
            self.log_message.emit(f"✓ Temperatura estabilizada em {t_dut:.1f}°C")
            self._start_next_corner()

    def _start_next_corner(self):
        if self._corner_idx >= len(config.CORNERS_V):
            self._start_sweep()
            return
        corner_v = config.CORNERS_V[self._corner_idx]
        self._current_result = CornerResult(voltage_cmd=corner_v)
        self.log_message.emit(
            f"─── Corner {self._corner_idx + 1}/{len(config.CORNERS_V)}: "
            f"PSU → {corner_v:.3f} V ───"
        )
        self._psu.set_voltage(corner_v)
        self._settle_ticks   = 0
        self._settle_timeout = 0
        self._set_phase(Phase.CORNER_SETTLING)

    def _do_corner_settling(self, v_dut: float):
        self._settle_timeout += 1
        target_v = self._current_result.voltage_cmd
        if v_dut > 0 and abs(v_dut - target_v) <= config.VOLT_SETTLE_TOL_V:
            self._settle_ticks += 1
        else:
            self._settle_ticks = 0

        if self._settle_ticks >= config.SETTLE_TICKS:
            self._sample_ticks = 0
            self.log_message.emit(
                f"✓ VCCINT estável: {v_dut:.3f} V (alvo {target_v:.3f} V)"
            )
            self._set_phase(Phase.CORNER_SAMPLING)
            return

        if self._settle_timeout >= config.SETTLE_TIMEOUT_TICKS:
            self.log_message.emit(
                f"AVISO: timeout estabilização — VCCINT={v_dut:.3f} V ≈ {target_v:.3f} V. Prosseguindo."
            )
            self._sample_ticks = 0
            self._set_phase(Phase.CORNER_SAMPLING)

    def _do_corner_sampling(self, v_dut, s_dut, fail, wrong, err, elapsed, data):
        r = self._current_result
        r.vccint_list.append(v_dut)
        r.slack_list.append(s_dut)
        if fail:       r.fail_any     = True
        r.wrong_total  += wrong
        r.errcnt_total += err
        self._sample_ticks += 1

        if self._logger:
            self._logger.write_row({
                **data,
                'phase':        f'CORNER_{r.voltage_cmd:.2f}V',
                'corner_v_cmd': f'{r.voltage_cmd:.3f}',
                'notes':        'FAIL' if (fail or wrong > 0 or err > 0) else '',
            })

        if self._sample_ticks >= config.SAMPLES_PER_CORNER:
            has_error = r.fail_any or r.wrong_total > 0 or r.errcnt_total > 0
            status    = "FALHA" if has_error else "OK"
            self.log_message.emit(
                f"Corner {r.voltage_cmd:.3f} V → "
                f"VCCINT={r.vccint_mean:.3f} V  "
                f"slack={r.slack_mean:.1f} cnt [{r.slack_min}…{r.slack_max}]  "
                f"fail={int(r.fail_any)}  wrong={r.wrong_total}  err={r.errcnt_total}  "
                f"[{status}]"
            )
            self._corner_results.append(r)
            self.corner_done.emit(self._corner_idx, r)
            self._corner_idx += 1
            self._start_next_corner()

    def _start_sweep(self):
        # Start one step below the lowest corner
        self._sweep_v = round(config.CORNERS_V[-1] - config.SWEEP_STEP_V, 4)
        self.log_message.emit(
            f"─── Todos os corners concluídos. "
            f"Iniciando varredura descendente a partir de {self._sweep_v:.3f} V ───"
        )
        self._apply_sweep_voltage()

    def _apply_sweep_voltage(self):
        if self._sweep_v < config.SWEEP_MIN_V:
            self.log_message.emit(
                f"Varredura chegou ao limite mínimo ({config.SWEEP_MIN_V:.2f} V) sem falha."
            )
            self._shutdown(had_failure=False, msg="Nenhuma falha detectada na faixa varrida.")
            return
        self.log_message.emit(f"Sweep → {self._sweep_v:.3f} V")
        self._psu.set_voltage(self._sweep_v)
        self._settle_ticks       = 0
        self._settle_timeout     = 0
        self._sweep_sample_ticks = 0
        self._set_phase(Phase.SWEEP_SETTLING)

    def _do_sweep_settling(self, v_dut: float):
        self._settle_timeout += 1
        if v_dut > 0 and abs(v_dut - self._sweep_v) <= config.VOLT_SETTLE_TOL_V:
            self._settle_ticks += 1
        else:
            self._settle_ticks = 0

        if self._settle_ticks >= config.SETTLE_TICKS:
            self._sweep_sample_ticks = 0
            self._set_phase(Phase.SWEEP_SAMPLING)
            return

        if self._settle_timeout >= config.SETTLE_TIMEOUT_TICKS:
            self.log_message.emit(
                f"AVISO: timeout estabilização sweep — VCCINT={v_dut:.3f} V. Prosseguindo."
            )
            self._sweep_sample_ticks = 0
            self._set_phase(Phase.SWEEP_SAMPLING)

    def _do_sweep_sampling(self, v_dut, s_dut, fail, wrong, err, elapsed, data):
        self._sweep_sample_ticks += 1
        # Error = adder wrong results or error count is non-zero; also capture fail latch
        error = bool(wrong > 0 or err > 0 or fail)
        self.sweep_tick.emit(self._sweep_v, s_dut, error)

        if self._logger:
            self._logger.write_row({
                **data,
                'phase':        'SWEEP',
                'corner_v_cmd': f'{self._sweep_v:.3f}',
                'notes':        'ERROR_DETECTED' if error else '',
            })

        if error:
            self.log_message.emit(
                f"✗ FALHA DETECTADA — "
                f"V_cmd={self._sweep_v:.3f} V  VCCINT={v_dut:.3f} V  "
                f"slack={s_dut}  fail={fail}  wrong={wrong}  err={err}"
            )
            self._failure_volt = self._sweep_v
            self._shutdown(
                had_failure=True,
                msg=(
                    f"Tensão de falha: {self._sweep_v:.3f} V  "
                    f"(VCCINT medido: {v_dut:.3f} V)"
                ),
            )
            return

        if self._sweep_sample_ticks >= config.SWEEP_SAMPLE_TICKS:
            self._sweep_v = round(self._sweep_v - config.SWEEP_STEP_V, 4)
            self._apply_sweep_voltage()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_phase(self, phase: Phase):
        self._phase = phase
        self.phase_changed.emit(phase.value)

    def _shutdown(self, had_failure: bool, msg: str):
        self._timer.stop()
        if config.ARDUINO_ENABLED and self._arduino.is_ready:
            self._arduino.stop_test_oven()
        if config.PSU_ENABLED and self._psu.is_running:
            self._psu.turn_off()
        if self._logger:
            self._logger.write_summary(self._corner_results, self._failure_volt)
            self._logger.close()
            self._logger = None
        self._set_phase(Phase.DONE)
        self.log_message.emit(f"=== TESTE CONCLUÍDO === {msg}")
        self.test_finished.emit(had_failure, msg)
