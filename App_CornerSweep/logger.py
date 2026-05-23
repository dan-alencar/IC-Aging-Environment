import csv
import os
from datetime import datetime

_FIELDS = [
    'timestamp', 'elapsed_s', 'phase', 'corner_v_cmd',
    'dut_temp_c', 'oven_temp_c',
    'dut_volt_v', 'psu_volt_v', 'psu_curr_a',
    'dut_slack', 'dut_fail', 'dut_wrong', 'dut_correct', 'dut_error_count',
    'notes',
]


class CornerSweepLogger:
    def __init__(self, log_folder, test_name, target_temp_c, corner_voltages, sweep_step):
        os.makedirs(log_folder, exist_ok=True)
        ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in test_name)
        self.filepath = os.path.join(log_folder, f"CornerSweep_{safe}_{ts}.csv")

        self._fh = open(self.filepath, 'w', newline='', encoding='utf-8', buffering=1)
        # Metadata header (comment lines — safe to strip with pandas comment='#')
        lines = [
            "# Corner Sweep Test",
            f"# Test:            {test_name}",
            f"# Date:            {datetime.now().isoformat()}",
            f"# Target DUT Temp: {target_temp_c} °C",
            f"# Corner voltages: {corner_voltages} V",
            f"# Sweep step:      {sweep_step} V",
            f"# Protocol:        'T'/0x54 trigger, 15-byte LE packet",
            "#",
        ]
        self._fh.write("\n".join(lines) + "\n")

        self._wr = csv.DictWriter(self._fh, fieldnames=_FIELDS, extrasaction='ignore')
        self._wr.writeheader()

    def write_row(self, row: dict):
        self._wr.writerow({k: row.get(k, '') for k in _FIELDS})

    def write_summary(self, corner_results, failure_volt):
        """Append a human-readable summary block after the data rows."""
        self._fh.write('\n#\n# === SUMMARY ===\n')
        self._fh.write(
            '# Corner_V_cmd, VCCINT_mean_V, Slack_mean, Slack_min, Slack_max, '
            'Fail, Wrong_total, ErrCnt_total\n'
        )
        for r in corner_results:
            status = "FAIL" if (r.fail_any or r.wrong_total > 0 or r.errcnt_total > 0) else "OK"
            self._fh.write(
                f'# {r.voltage_cmd:.3f}, {r.vccint_mean:.4f}, '
                f'{r.slack_mean:.1f}, {r.slack_min}, {r.slack_max}, '
                f'{int(r.fail_any)}, {r.wrong_total}, {r.errcnt_total}  [{status}]\n'
            )
        self._fh.write(
            f'# Failure voltage: {failure_volt:.3f} V\n'
            if failure_volt is not None
            else '# No failure detected within sweep range\n'
        )
        self._fh.flush()

    def close(self):
        if not self._fh.closed:
            end = datetime.now().isoformat()
            self._fh.write(f'# Closed: {end}\n')
            self._fh.close()
