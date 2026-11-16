#!/usr/bin/env python3
"""Testa o fpga_link_core.c (compilado no PC) contra o protocol_v2.py do D&T Monitor.

    python3 tests_host/test_fl_host.py      (a partir da pasta do projeto)
"""
import os, random, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
APP = os.environ.get("DT_MONITOR_DIR", os.path.expanduser(
    "~/Documentos/GitHub/IC-Aging-Environment/D&T 2027/10_DT_Monitor"))
sys.path.insert(0, APP)
import protocol_v2 as p          # noqa: E402
import legacy_link as ll         # noqa: E402

def build():
    exe = os.path.join(tempfile.mkdtemp(), "fl_host")
    subprocess.run(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-O1",
                    "-I", os.path.join(PROJ, "Core/Inc"),
                    os.path.join(HERE, "fl_host.c"), os.path.join(PROJ, "Core/Src/fpga_link_core.c"),
                    "-o", exe], check=True)
    return exe

def sensor(i):
    return p.FpgaSensor(window_id=i, sweep_count=8000 + i, slack_last=409, slack_min=408,
                        slack_max=411, slack_sum=409 * (8000 + i), slack_sumsq=409 * 409 * (8000 + i),
                        temp_raw=0xA2C0 + i, vccint_raw=0x4880, vccaux_raw=0, vccbram_raw=0,
                        flags=0x43, lock_loss=0)

def info():
    return p.FpgaInfo(dna=bytes.fromhex("40020000016069492D020185")[::-1], usr_access=0x20C90A4D,
                      rtl_version=2, sweep_mode=1, window_ms=1000, ps_step_fs=19841, sysmon_ref=0)

def main():
    exe = build()
    rng = random.Random(1)
    stream = []          # (t_ms, byte)
    expect = []          # quadros que devem sair
    t = 0
    def put(data, dt_byte=0):
        nonlocal t
        for b in data:
            stream.append((t, b)); t += dt_byte
    seq = 0
    def frame(ftype, payload):
        nonlocal seq
        f = p.encode_frame(ftype, seq, payload); seq = (seq + 1) & 0xFF
        return f
    # 1. quadros normais, 1 por "segundo", com INFO no começo
    f = frame(p.T_FPGA_INFO, info().pack()); put(f); expect.append(f); t += 1000
    for i in range(1, 6):
        f = frame(p.T_FPGA_SENSOR, sensor(i).pack()); put(f); expect.append(f); t += 1000
    # 2. lixo entre quadros, inclusive A5 soltos e "A5 A5 5A"
    put(bytes([0x00, 0xA5, 0x11, 0xA5])); t += 50
    f = frame(p.T_FPGA_SENSOR, sensor(6).pack()); put(bytes([0xA5]) + f); expect.append(f); t += 1000
    # 3. CRC errado: some
    f = bytearray(frame(p.T_FPGA_SENSOR, sensor(7).pack())); f[20] ^= 0x01; put(f); t += 1000
    # 4. quadro cortado no meio + silêncio: o próximo não pode se perder
    f = frame(p.T_FPGA_SENSOR, sensor(8).pack()); put(f[:20]); t += 1000
    f = frame(p.T_FPGA_SENSOR, sensor(9).pack()); put(f); expect.append(f); t += 1000
    # 5. dois quadros colados (SENSOR + INFO, como no fim de cada 60 janelas)
    f1 = frame(p.T_FPGA_SENSOR, sensor(10).pack()); f2 = frame(p.T_FPGA_INFO, info().pack())
    put(f1 + f2); expect += [f1, f2]; t += 1000
    # 6. cabeçalho inválido (LEN > 200 e VER errado)
    put(bytes([0xA5, 0x5A, 0x02, 0x01, 0x00, 0xFF])); t += 10
    put(bytes([0xA5, 0x5A, 0x03, 0x01, 0x00, 0x04])); t += 1000
    # 7. bytes espaçados de 1 ms (dentro do limite de 5 ms)
    f = frame(p.T_FPGA_SENSOR, sensor(11).pack()); put(f, dt_byte=1); expect.append(f); t += 1000
    # 8. muitos quadros aleatórios com ruído
    for i in range(12, 200):
        f = frame(p.T_FPGA_SENSOR, sensor(i).pack())
        if rng.random() < 0.1:
            put(bytes(rng.getrandbits(8) for _ in range(rng.randrange(1, 8)))); t += 50
        put(f); expect.append(f); t += 1000
    # 9. quadro entregue em dois lotes, 8 ms um do outro (meio do buffer do DMA no começo
    #    de uma rajada SENSOR + INFO): não pode ser cortado
    f1 = frame(p.T_FPGA_SENSOR, sensor(200).pack()); f2 = frame(p.T_FPGA_INFO, info().pack())
    put((f1 + f2)[:10]); t += 8
    put((f1 + f2)[10:]); expect += [f1, f2]; t += 1000

    inp = "".join(f"{tm} {b:02x}\n" for tm, b in stream)
    out = subprocess.run([exe], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()
    end = out[-1]
    got = []
    for line in out[:-1]:
        fields = ll.parse_tel(line, kind="FPG")          # checksum e formato, como no app
        raw = bytes.fromhex(fields["Hx"])
        fr = p.FrameParser().feed(raw)
        assert len(fr) == 1, line
        p.decode(fr[0])                                  # payload decodificável
        got.append(raw)
    assert got == expect, f"{len(got)} quadros, esperado {len(expect)}"
    cnt = dict(kv.split("=") for kv in end.split()[1:])
    assert int(cnt["ok"]) == len(expect), cnt
    assert int(cnt["ce"]) >= 1 and int(cnt["he"]) == 2 and int(cnt["gaps"]) >= 1, cnt   # gaps: o corte do cenário 4 e lixo aleatório que termina em A5
    print(f"OK: {len(got)} quadros repassados iguais aos originais; contadores {cnt}")
    print("exemplo:", out[1][:120], "...")

if __name__ == "__main__":
    main()
