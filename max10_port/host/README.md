# host/ — PC-side acquisition software

*[Leia em português](README.pt-BR.md)*

Empty for now. This is where front F4 (telemetry and acquisition) puts the PC-side
application once the transport decision (JTAG UART vs. external USB-serial module —
see the plan document, Section 4.4, task 1) is made.

**Suggested starting point:** fork `../../App_Nexys/` rather than starting from
scratch. It already has the pieces F4 needs to preserve or adapt:

- `App_Nexys/workers.py` — `DUTWorker` (packet polling), `ArduinoWorker` (oven PID
  serial protocol), `TestSequencer` (orchestration, CSV row assembly, safety limits).
  The packet-parsing logic in `DUTWorker.poll_data()` is the part that changes most —
  new transport, and no XADC-derived VCCINT field to parse until front F3 defines
  what replaces it.
- `App_Nexys/logger.py` — the CSV format to stay compatible with. The plan document
  is explicit (Section 4.4, task 2) that CSV compatibility with the existing
  `analysis/` pipeline is a requirement, not a nice-to-have — it's what makes the
  Artix-7 vs. MAX10 comparison in front F6 direct instead of requiring reconciliation
  of two different formats.
- `App_Nexys/main_window.py` — Qt UI structure (tabs, live plots, log panel) if the
  new app keeps a GUI at all; a headless/CLI acquisition tool is also a legitimate
  choice for a research-only tool and may be simpler to keep robust through
  multi-day campaigns (see the plan's 72-hour resilience test, Section 4.4, task 5).

Do not copy `App_Nexys/config.py`'s hardcoded serial IDs or Vivado paths — those are
specific to the existing Nexys4 lab setup.
