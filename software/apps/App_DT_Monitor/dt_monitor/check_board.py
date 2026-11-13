"""check-board: bring-up check of one board (port of the colleague's verificar_hub.py).

    dt-monitor check-board /dev/serial/by-id/...STLINK...-if02 --board A [--seconds 20]
    dt-monitor check-board PORT --board A --program bitstreams/fbs_aging_top.bit --vivado vivado

Close the app first (the service owns the ports). For the board:
  1. INFO from the STM32 and the FPGA platform, checked against the registry (DNA, UID),
     and the bitstream's USR_ACCESS against --program's .bit; with --program the FPGA is
     programmed over JTAG (the registry's cable) if it is not running that file;
  2. listens --seconds and checks every frame type: AGING_INFO, AGING_WINDOW (sweeps, slack,
     flags), all chains in every window and chain 0 equal to AGING_WINDOW, SYSMON, PWR_TELEM
     (state, die known), LINK_STATUS (errors), RELAY_STATUS (drops) and the host's own
     CRC/sequence counters.
Exit status 0 when everything passes.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from fpgaging_bsp import protocol as P
from fpgaging_bsp.bench import Registry
from fpgaging_bsp.bench.identity import bitfile_identity, check_identity
from fpgaging_bsp.devices import Platform, Supervisor
from fpgaging_bsp.link import CommandError, Link, LinkTimeout, open_serial

from . import protocol_aging as A
from .stats import window_stats


class Report:
    def __init__(self):
        self.lines: List[str] = []
        self.failed = 0

    def ok(self, cond: bool, text: str) -> bool:
        self.lines.append(("  ok    " if cond else "  FAIL  ") + text)
        self.failed += not cond
        return cond

    def note(self, text: str) -> None:
        self.lines.append("  note  " + text)


def check(link: Link, board: str, registry: Registry, seconds: float = 20.0, bitfile: Optional[Path] = None,
          vivado: Optional[str] = None, n_chains: int = 9) -> Report:
    rep = Report()
    sup, plat = Supervisor(link), Platform(link)
    try:
        si = sup.info()
    except (LinkTimeout, CommandError) as e:
        si = None
        rep.ok(False, f"STM32 INFO: {e}")
    try:
        pi = plat.info()
    except (LinkTimeout, CommandError) as e:
        pi = None
        rep.ok(False, f"FPGA platform INFO: {e}")
    ident = check_identity(board, registry, pi, si, getattr(link.t, "port", "") or "",
                           bitfile.parent if bitfile else None)
    for p in ident.problems:
        rep.ok(False, f"identity: {p}")
    for w in ident.warnings:
        rep.note(f"identity: {w}")
    if not ident.problems:
        rep.ok(True, f"identity: DNA {ident.dna}, UID {ident.stm32_uid}, USR_ACCESS {ident.usr_access}")
    if bitfile is not None:
        want = bitfile_identity(bitfile).get("usr_access")
        if pi is None or ident.usr_access != want:
            reg = registry.get(board)
            if vivado and reg and reg.jtag_usb:
                from fpgaging_bsp.bench import jtag
                rep.note(f"programming {bitfile.name} over JTAG (USB {reg.jtag_usb})")
                jtag.program(vivado, reg.jtag_usb, 0, bitfile, bitfile.with_suffix(".ltx")
                             if bitfile.with_suffix(".ltx").exists() else None)
                time.sleep(2.0)
                pi = plat.info()
                rep.ok(f"0x{pi.build_time:08X}" == want, f"after programming USR_ACCESS 0x{pi.build_time:08X}")
            else:
                rep.ok(False, f"the FPGA is not running {bitfile.name} (USR_ACCESS {want}); "
                              "pass --vivado and set jtag_usb in the registry to program it")

    # listen
    frames = []
    link.subscribe(frames.append)
    try:
        link.request(P.Node.FPGA_APP, A.AgingGetInfo(), check=False)
    except (LinkTimeout, CommandError):
        pass
    time.sleep(seconds)
    by: Dict[str, list] = {}
    for f in frames:
        try:
            by.setdefault(f.type_name, []).append(f.msg)
        except ValueError:
            by.setdefault("undecodable", []).append(f)
    info = by.get("AGING_INFO", [])
    if rep.ok(bool(info), f"AGING_INFO ({len(info)})") and info:
        i = info[-1]
        rep.note(f"payload v{i.rtl_version}: {i.n_chains} chains, window {i.window_ms} ms, "
                 f"mode {A.SweepMode(i.sweep_mode).name}, {i.n_ro} ring oscillators")
    wins = by.get("AGING_WINDOW", [])
    rep.ok(len(wins) >= max(1, int(seconds) - 3), f"AGING_WINDOW: {len(wins)} in {seconds:.0f} s")
    ids = [w.window_id for w in wins]
    rep.ok(all(b == a + 1 for a, b in zip(ids, ids[1:])), "window ids consecutive")
    chains = by.get("AGING_CHAIN", [])
    for w in wins[1:]:
        cs = [c for c in chains if c.window_id == w.window_id]
        got = {c.chain for c in cs}
        if not rep.ok(set(range(n_chains)) <= got, f"window {w.window_id}: chains {sorted(got)}"):
            continue
        c0 = next(c for c in cs if c.chain == 0)
        rep.ok((c0.sweeps, c0.min, c0.max, c0.sum, c0.sumsq) == (w.sweeps, w.min, w.max, w.sum, w.sumsq),
               f"window {w.window_id}: chain 0 equals AGING_WINDOW")
        bad = A.AgingFlags.NO_ALARM | A.AgingFlags.PS_TIMEOUT | A.AgingFlags.LOCK_LOST
        rep.ok(not (w.flags & bad), f"window {w.window_id}: flags {A.AgingFlags(w.flags)!r}")
    if wins:
        w = wins[-1]
        mean, std = window_stats(w.sweeps, w.sum, w.sumsq)
        rep.note(f"chain 0: {w.sweeps} sweeps, slack {mean:.2f} (std {std:.2f}, {w.min}-{w.max})"
                 if mean is not None else "chain 0: no sweeps")
    sm = by.get("SYSMON", [])
    rep.ok(bool(sm), f"SYSMON ({len(sm)})")
    pw = by.get("PWR_TELEM", [])
    if rep.ok(bool(pw), f"PWR_TELEM ({len(pw)})") and pw:
        last = pw[-1]
        rep.ok(last.state in (P.State.NORMAL, P.State.OUTPUT_OFF), f"STM32 state {P.State(last.state).name}")
        rep.ok(not last.flags & P.PwrFlags.DIE_UNKNOWN, "die temperature known to the STM32")
    ls = by.get("LINK_STATUS", [])
    if ls:
        errs = sum(p.crc_err + p.hdr_err + p.fifo_drop for p in ls[-1].ports)
        rep.ok(errs == 0, f"FPGA link counters: {errs} errors/drops")
    rs = by.get("RELAY_STATUS", [])
    if rs:
        drops = sum(d.drops for d in rs[-1].dirs)
        rep.ok(drops == 0, f"ST-LINK relay: {drops} drops")
    st = link.decoder.stats
    rep.ok(st.crc_err == 0 and st.hdr_err == 0 and link.tracker.total_lost == 0,
           f"host link: {st.crc_err} CRC, {st.hdr_err} header errors, {link.tracker.total_lost} lost")
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dt-monitor check-board", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", help="serial port (ST-LINK VCP or J9), or SIM for the simulator")
    ap.add_argument("--board", required=True, help="registry name (A, B, ...)")
    ap.add_argument("--baud", type=int, default=P.BAUD_DEFAULT)
    ap.add_argument("--seconds", type=float, default=20.0)
    ap.add_argument("--program", type=Path, help=".bit to run (programmed over JTAG if needed)")
    ap.add_argument("--vivado", help="vivado executable for --program")
    ap.add_argument("--registry", type=Path)
    a = ap.parse_args(argv)
    sim = None
    if a.port.upper() == "SIM":
        from fpgaging_bsp.sim import Simulation
        from .sim_app import AgingAppModel
        sim = Simulation(boards=1, app_factory=AgingAppModel).start()
        t = sim.transport(0, "stlink")
    else:
        t = open_serial(a.port, a.baud)
    link = Link(t).start()
    try:
        rep = check(link, a.board, Registry.load(a.registry), a.seconds, a.program, a.vivado)
    finally:
        link.close()
        if sim:
            sim.stop()
    print(f"board {a.board} on {a.port}:")
    print("\n".join(rep.lines))
    print("PASS" if not rep.failed else f"FAIL ({rep.failed})")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
