# -*- coding: utf-8 -*-
"""
Multi-sensor packet protocol (experimental-multi-sensor branch).

Matches vivado/aging_study_nexys4ddr/src/rtl/uart/multi_sensor_stream.sv --
see that file's header comment for the exact byte layout. This replaces
the legacy 15-byte [TEMP][SLACK][VOLT][FAIL][WRONG][CORRECT][ERR_CNT]
packet used on main/inverter-chain-sensor: this branch's RTL no longer has
a functional canary to report (wrong/correct/error_count/fail are gone),
and slack/alarm are now one value per channel instead of scalars.

Kept as its own copy here (not imported from App_FPGAging_Slack_Sensor)
following this repo's existing convention of each App_* folder being
self-contained.
"""

MULTI_SYNC0 = 0xAA
MULTI_SYNC1 = 0x55
MULTI_NUM_CHANNELS = 4
MULTI_PKT_LEN = 10 + 2 * MULTI_NUM_CHANNELS  # sync(2)+len(1)+temp(3)+vcc(3)+slack(2N)+alarm(1)+cksum(1)


def parse_multi_sensor_packet(pkt: bytes, num_channels: int = MULTI_NUM_CHANNELS):
    """
    Decodes one multi_sensor_stream.sv frame. `pkt` must be exactly
    MULTI_PKT_LEN bytes, starting at the sync bytes.

    Returns a dict with 'temp_raw' (24-bit, millidegrees C), 'vccint_raw'
    (24-bit, millivolts), 'slack' (list[int], one per channel), 'alarm'
    (list[bool], one per channel) -- or None if the sync bytes or checksum
    don't match.
    """
    expected_len = 10 + 2 * num_channels
    if len(pkt) != expected_len:
        return None
    if pkt[0] != MULTI_SYNC0 or pkt[1] != MULTI_SYNC1:
        return None

    len_field    = pkt[2]
    temp_bytes   = pkt[3:6]
    vccint_bytes = pkt[6:9]
    slack_bytes  = pkt[9:9 + 2 * num_channels]
    alarm_byte   = pkt[9 + 2 * num_channels]
    checksum     = pkt[10 + 2 * num_channels]

    calc = len_field
    for b in temp_bytes:
        calc ^= b
    for b in vccint_bytes:
        calc ^= b
    for b in slack_bytes:
        calc ^= b
    calc ^= alarm_byte
    calc &= 0xFF

    if calc != checksum:
        return None

    return {
        'temp_raw':   int.from_bytes(temp_bytes, 'little'),
        'vccint_raw': int.from_bytes(vccint_bytes, 'little'),
        'slack':      [int.from_bytes(slack_bytes[2 * i:2 * i + 2], 'little')
                        for i in range(num_channels)],
        'alarm':      [bool((alarm_byte >> i) & 1) for i in range(num_channels)],
    }
