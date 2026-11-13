"""dt-monitor: the IC-Aging burn-in app on the fbs bench kit.

    dt-monitor gui [BENCH]                 the window (a client of fbs-service)
    dt-monitor service --config BENCH.yaml fbs-service with this app's plugins (same as fbs service)
    dt-monitor corners BENCH [...]         slack corners through the service
    dt-monitor oven-test PORT|SIM [...]    oven test with interlocks (service stopped)
    dt-monitor check-board PORT|SIM --board A [...]   bring-up check (service stopped)
"""
import sys


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "gui":
        from .gui import main as m
    elif cmd == "service":
        from fpgaging_bsp.cli import main as fbs
        return fbs(["service"] + rest)
    elif cmd == "corners":
        from .corners import main as m
    elif cmd == "oven-test":
        from .oven_test import main as m
    elif cmd == "check-board":
        from .check_board import main as m
    else:
        print(f"unknown command {cmd!r}\n{__doc__}", file=sys.stderr)
        return 2
    return m(rest)


if __name__ == "__main__":
    sys.exit(main())
