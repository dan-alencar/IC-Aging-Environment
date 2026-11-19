#!/usr/bin/env python3
"""
Monitor UART do sensor de aging (MAX10 / DE10-Lite).

Formato do pacote (5 bytes, enviado a cada 100 ms, 115200 baud, 8N1):
    byte 0: 0xAA                      (sincronismo)
    byte 1: slack_count[15:8]
    byte 2: slack_count[7:0]
    byte 3: status   bit0 alarm      bit1 calibrated  bit2 valid
                     bit3 sat_hi     bit4 at_origin   bit5 timeout
                     bit6 pll_lost   bit7 seq (alterna a cada medicao concluida)
    byte 4: checksum = byte1 ^ byte2 ^ byte3

Interpretacao: so use slack_count quando valid=1 e sat_hi=0.
  sat_hi=1    leitura saturada/ambigua (cadeia mais rapida que o catcher)
  at_origin=1 alarme ja alto sem deslocar a fase (medida inutil)
  timeout=1   MAX_STEPS passos sem alarme (sensor/cadeia sem resposta)
  pll_lost=1  a PLL perdeu o lock desde o ultimo reset (desconfie dos dados)

Uso:
    python uart_monitor.py --selftest          # testa o decodificador, sem placa
    python uart_monitor.py COM5                # Windows
    python uart_monitor.py /dev/ttyUSB0        # Linux
    python uart_monitor.py COM5 --csv log.csv  # grava tambem em CSV

Requer: pip install pyserial   (so para ler a porta; o --selftest nao precisa)
"""

import argparse
import csv
import sys
from datetime import datetime

STEP_PS = 178.571      # 1/8 do periodo do VCO de 700 MHz (aging_pll.v: vco_phase_shift_step=179 e arredondamento)
SYNC = 0xAA
FRAME_LEN = 5


def parse_frames(buf):
    """Extrai pacotes validos de 'buf' (bytearray).

    Devolve (lista_de_pacotes, bytes_descartados). Consome de 'buf' tudo o
    que foi processado e deixa nele apenas o que ainda pode virar pacote.
    Um 0xAA dentro dos dados nao quebra o sincronismo: se o checksum do
    candidato nao bater, descarta so aquele byte e procura o proximo 0xAA.
    """
    frames = []
    discarded = 0
    while True:
        idx = buf.find(bytes([SYNC]))
        if idx < 0:
            discarded += len(buf)
            buf.clear()
            break
        if idx > 0:
            discarded += idx
            del buf[:idx]
        if len(buf) < FRAME_LEN:
            break                      # pacote incompleto: espera mais bytes
        b1, b2, b3, b4 = buf[1], buf[2], buf[3], buf[4]
        if (b1 ^ b2 ^ b3) == b4:
            slack = (b1 << 8) | b2
            frames.append({
                "slack_count": slack,
                "alarm": b3 & 0x01,
                "calibrated": (b3 >> 1) & 0x01,
                "valid": (b3 >> 2) & 0x01,
                "sat_hi": (b3 >> 3) & 0x01,
                "at_origin": (b3 >> 4) & 0x01,
                "timeout": (b3 >> 5) & 0x01,
                "pll_lost": (b3 >> 6) & 0x01,
                "seq": (b3 >> 7) & 0x01,
            })
            del buf[:FRAME_LEN]
        else:
            discarded += 1             # falso sincronismo: descarta o 0xAA
            del buf[:1]
    return frames, discarded


def fmt(frame):
    n = frame["slack_count"]
    warn = [k for k in ("sat_hi", "at_origin", "timeout", "pll_lost") if frame[k]]
    if not frame["valid"]:
        warn.insert(0, "INVALIDO")
    return (f"slack_count={n} (0x{n:04X}) = {n * STEP_PS / 1000:.2f} ns | "
            f"valid={frame['valid']} seq={frame['seq']} calibrated={frame['calibrated']} "
            f"alarm={frame['alarm']}" + (f" | ATENCAO: {', '.join(warn)}" if warn else ""))


def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(f"  [{'OK' if cond else 'FALHA'}] {name}")
        ok = ok and cond

    print("Autoteste do decodificador:")

    def mk(slack, status):
        h, l = slack >> 8, slack & 0xFF
        return bytearray([0xAA, h, l, status, h ^ l ^ status])

    # 1) pacote v3 valido: slack 1023 (0x03FF), valid=1 calibrated=1 seq=1 -> status 0x86
    fr, _ = parse_frames(mk(1023, 0b10000110))
    check("v3: slack 1023, valid=1 calibrated=1 seq=1, sem flags de erro",
          len(fr) == 1 and fr[0]["slack_count"] == 1023 and fr[0]["valid"] == 1
          and fr[0]["seq"] == 1 and fr[0]["calibrated"] == 1
          and not (fr[0]["sat_hi"] or fr[0]["at_origin"] or fr[0]["timeout"] or fr[0]["pll_lost"]))
    print("     ", fmt(fr[0]))
    # 1b) saturado (pacote real do simulador: AA 04 29 0E ..) valid=1 sat_hi=1
    fr, _ = parse_frames(mk(1065, 0b00001110))
    check("v3: slack 1065 com sat_hi=1 e avisado", len(fr) == 1 and fr[0]["sat_hi"] == 1
          and "sat_hi" in fmt(fr[0]))
    print("     ", fmt(fr[0]))
    # 1c) timeout / pll_lost
    fr, _ = parse_frames(mk(0, 0b01101000))
    check("v3: timeout=1 pll_lost=1 valid=0 avisados",
          len(fr) == 1 and fr[0]["timeout"] == 1 and fr[0]["pll_lost"] == 1 and fr[0]["valid"] == 0
          and "INVALIDO" in fmt(fr[0]))

    # 2) lixo antes do primeiro pacote + dois pacotes seguidos
    buf = bytearray([0x12, 0x34] + [0xAA, 0x03, 0xFC, 0x03, 0xFC] * 2)
    fr, disc = parse_frames(buf)
    check("lixo no inicio descartado, 2 pacotes lidos", len(fr) == 2 and disc == 2)

    # 3) 0xAA dentro dos dados (slack_count = 0x00AA): checksum = 0x00^0xAA^0x03 = 0xA9
    buf = bytearray([0xAA, 0x00, 0xAA, 0x03, 0xA9])
    fr, _ = parse_frames(buf)
    check("0xAA nos dados nao quebra o pacote (slack 170)",
          len(fr) == 1 and fr[0]["slack_count"] == 170)

    # 4) checksum errado e rejeitado
    buf = bytearray([0xAA, 0x03, 0xFC, 0x03, 0x00])
    fr, _ = parse_frames(buf)
    check("checksum errado e descartado", len(fr) == 0)

    # 5) pacote chegando em pedacos
    buf = bytearray([0xAA, 0x03, 0xFC])
    fr1, _ = parse_frames(buf)
    buf.extend([0x03, 0xFC])
    fr2, _ = parse_frames(buf)
    check("pacote incompleto espera o resto", len(fr1) == 0 and len(fr2) == 1)

    print("Resultado:", "tudo OK" if ok else "HOUVE FALHAS")
    return 0 if ok else 1


def run(port, baud, csv_path):
    try:
        import serial  # pyserial
    except ImportError:
        sys.exit("Falta o pyserial. Instale com:  pip install pyserial")

    try:
        ser = serial.Serial(port, baud, timeout=1)
    except serial.SerialException as e:
        sys.exit(f"Nao consegui abrir {port}: {e}")

    writer = None
    fh = None
    if csv_path:
        fh = open(csv_path, "a", newline="", encoding="utf-8")
        writer = csv.writer(fh)
        if fh.tell() == 0:
            writer.writerow(["timestamp", "slack_count", "slack_ns",
                             "valid", "sat_hi", "at_origin", "timeout",
                             "pll_lost", "seq", "calibrated", "alarm"])

    print(f"Lendo {port} a {baud} baud (Ctrl+C para parar)...")
    buf = bytearray()
    total_bytes = 0
    last_report = datetime.now()
    try:
        while True:
            data = ser.read(64)
            if data:
                total_bytes += len(data)
                buf.extend(data)
                frames, _ = parse_frames(buf)
                for f in frames:
                    ts = datetime.now().isoformat(timespec="milliseconds")
                    print(ts, fmt(f))
                    if writer:
                        writer.writerow([ts, f["slack_count"],
                                         f"{f['slack_count'] * STEP_PS / 1000:.3f}",
                                         f["valid"], f["sat_hi"], f["at_origin"],
                                         f["timeout"], f["pll_lost"], f["seq"],
                                         f["calibrated"], f["alarm"]])
                        fh.flush()
            elif (datetime.now() - last_report).total_seconds() >= 3:
                # nada chegou: ajuda a diagnosticar
                print(f"(sem dados ha 3 s; bytes recebidos ate agora: {total_bytes})")
                last_report = datetime.now()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        ser.close()
        if fh:
            fh.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", nargs="?", help="porta serial, ex.: COM5 ou /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--csv", help="arquivo CSV para registrar as leituras")
    ap.add_argument("--selftest", action="store_true",
                    help="testa o decodificador sem precisar da placa")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if not args.port:
        ap.error("informe a porta serial (ou use --selftest)")
    run(args.port, args.baud, args.csv)


if __name__ == "__main__":
    main()
