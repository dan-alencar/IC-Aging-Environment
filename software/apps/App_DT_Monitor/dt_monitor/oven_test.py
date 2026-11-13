"""oven-test: the oven with interlocks (port of teste_forno.py), for firmware 2.0.

    dt-monitor oven-test PORT                      # PID heating to 45 degC, at most 8 min
    dt-monitor oven-test PORT --sp 45 --minutes 8
    dt-monitor oven-test PORT --monitor --minutes 5  # read only, heater off
    dt-monitor oven-test PORT --full --sp 70         # 100 % until close to sp, then follow 20 min

Close the app first (it owns the oven port). The script never changes the tuning: it reads
GET_CONFIG, sends SET_SP and START_TEST, reads GET_DATA every 2 s and ALWAYS ends with
STOP_TEST (also on errors, Ctrl+C and SIGTERM). It stops by itself when:
  - the reading fails for 10 s or leaves 0-130 degC (on 05/11/2026 the NTC read -78 degC);
  - the firmware reports a fault (EVENT,FAULT,... or a FAULT state);
  - heating: the oven passes sp + 5 degC or 60 degC, or reaches sp;
  - heating and --full: the output stays above 25 % for a whole --rise-min window with
    less than 2 degC of rise (not enough power);
  - the time is up.
Heating is compared with the FOPDT model of the paper (K 1.56 degC/%, theta 150.6 s,
tau 1307.2 s) driven by the measured output. With firmware 2.0 the temperature updates while
idle, so --monitor needs no test running. --full asks for sp + 40 degC (capped at 130), so
the output saturates, and stops the test once the oven is within --margin of sp.
Results go to test_logs/oven_tests/oven_<date>.csv.
"""
from __future__ import annotations

import argparse
import csv
import math
import signal
import sys
import time
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from fpgaging_bsp.service.oven import OvenClient, OvenError

K, THETA_S, TAU_S = 1.56, 150.6, 1307.2
LIMIT_C = 60.0


def fopdt(samples: List[Tuple[float, float, float]]) -> List[float]:
    """Predicted temperature at each sample from the measured output (first-order + dead time)."""
    if not samples:
        return []
    y0 = samples[0][1]
    pred, y = [], 0.0
    for i, (t, _temp, _out) in enumerate(samples):
        if i:
            dt = t - samples[i - 1][0]
            delayed = next((o for (tt, _, o) in reversed(samples[:i]) if tt <= t - THETA_S), 0.0)
            y += (K * delayed - y) * (1 - math.exp(-dt / TAU_S))
        pred.append(y0 + y)
    return pred


def run(oven: OvenClient, sp: float, minutes: float, monitor: bool = False, full: bool = False,
        margin: float = 10.0, after_min: float = 20.0, rise_min: float = 10.0, period_s: float = 2.0,
        out: Optional[Path] = None, clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep, log=print) -> Tuple[str, List[Tuple[float, float, float]]]:
    """Returns (why it stopped, samples [(t_s, temp_c, output_pct)])."""
    stop_reason = "time up"
    samples: List[Tuple[float, float, float]] = []
    cfg = oven.get_config()
    log(f"oven: {cfg}")
    started = False
    heating = not monitor
    req = min(130.0, sp + 40.0) if full else sp
    t0 = clock()
    last_ok = t0
    heater_off_at: Optional[float] = None
    try:
        if heating:
            oven.set_setpoint(req)
            oven.start()
            started = True
            log(f"heating: setpoint {req:.1f} degC ({'full power' if full else 'PID'})")
        end = t0 + 60.0 * minutes
        while clock() < end:
            now = clock()
            try:
                d = oven.get_data()
                last_ok = now
            except OvenError as e:
                if now - last_ok > 10.0:
                    stop_reason = f"no reading for 10 s ({e})"
                    break
                sleep(period_s)
                continue
            t = d.temp_c
            samples.append((now - t0, t if t is not None else float("nan"), d.output_pct or 0.0))
            if t is None or not 0.0 <= t <= 130.0:
                stop_reason = f"reading out of range: {t}"
                break
            if d.state == "FAULT" or (d.fault and d.fault != "NONE"):
                stop_reason = f"firmware fault {d.fault}"
                break
            if heating and heater_off_at is None:
                if t > min(sp + 5.0, LIMIT_C if not full else 130.0):
                    stop_reason = f"oven at {t:.1f} degC, above the limit"
                    break
                if full and t >= sp - margin:
                    oven.stop()
                    heater_off_at = now
                    log(f"{t:.1f} degC: heater off, following the inertia for {after_min:.0f} min")
                    end = now + 60.0 * after_min
                elif not full and t >= sp:
                    stop_reason = "setpoint reached"
                    break
                win = [s for s in samples if s[0] >= samples[-1][0] - 60.0 * rise_min]
                if full and win and samples[-1][0] >= 60.0 * rise_min and all(s[2] > 25.0 for s in win) \
                        and win[-1][1] - win[0][1] < 2.0:
                    stop_reason = f"less than 2 degC in {rise_min:.0f} min at >25 % output (not enough power)"
                    break
            sleep(period_s)
    except KeyboardInterrupt:
        stop_reason = "interrupted"
    except OvenError as e:
        stop_reason = f"oven refused: {e}"
    finally:
        if started:
            try:
                oven.stop()
            except OvenError as e:
                log(f"STOP_TEST failed: {e}  -- switch the oven off by hand")
    if out is not None and samples:
        out.parent.mkdir(parents=True, exist_ok=True)
        pred = fopdt(samples)
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            f.write(f"# oven-test: sp {sp} degC, mode {'monitor' if monitor else 'full' if full else 'pid'}\n")
            f.write(f"# oven_config: {cfg}\n# stop_reason: {stop_reason}\n")
            w.writerow(["t_s", "oven_temp_c", "output_pct", "fopdt_temp_c"])
            for (ts, temp, o), p in zip(samples, pred):
                w.writerow([round(ts, 1), temp, o, round(p, 2)])
    log(f"stopped: {stop_reason}")
    return stop_reason, samples


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dt-monitor oven-test", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", help="oven serial port, or SIM")
    ap.add_argument("--sp", type=float, default=45.0)
    ap.add_argument("--minutes", type=float, default=8.0)
    ap.add_argument("--monitor", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--margin", type=float, default=10.0)
    ap.add_argument("--after-min", type=float, default=20.0)
    ap.add_argument("--rise-min", type=float, default=10.0)
    ap.add_argument("--out", type=Path, default=Path("test_logs/oven_tests"))
    a = ap.parse_args(argv)
    if a.full and a.sp > 70.0:
        ap.error("--full is limited to 70 degC")
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    if signal.getsignal(signal.SIGHUP) is not None:
        signal.signal(signal.SIGHUP, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    if a.port.upper() == "SIM":
        from fpgaging_bsp.service.oven import SimOven
        from fpgaging_bsp.sim import Simulation
        sim = Simulation(boards=1).start(speed=60.0)
        oven: OvenClient = SimOven(sim)
    else:
        from .oven import AsciiOven
        sim, oven = None, AsciiOven(a.port)
    out = a.out / time.strftime("oven_%Y%m%d_%H%M%S.csv")
    try:
        reason, _ = run(oven, a.sp, a.minutes, a.monitor, a.full, a.margin, a.after_min, a.rise_min, out=out,
                        clock=sim.clock.monotonic if sim else time.monotonic,
                        sleep=sim.clock.sleep if sim else time.sleep)
    finally:
        oven.close()
        if sim:
            sim.stop()
    print(f"log: {out}")
    return 0 if reason in ("time up", "setpoint reached") or reason.startswith("heater off") else 1


if __name__ == "__main__":
    sys.exit(main())
