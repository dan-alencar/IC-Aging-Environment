"""Gera o esquemático KiCad 7 do controle do forno (Arduino Nano 33 IoT + NTC + TIP31 + SSR).

    python3 gera_forno.py <pasta_de_saida>

Os símbolos vêm das bibliotecas do KiCad instaladas (/usr/share/kicad/symbols) e são
embutidos no arquivo; o SSR é um símbolo próprio com os terminais do LOTI 48D25A.
"""
import json
import math
import os
import sys
import uuid

import sexp
from sexp import Sym

LIBDIR = "/usr/share/kicad/symbols/"
PROJECT = "forno_controle"
ROOT = str(uuid.uuid4())

_libs = {}


def lib_symbol(lib, name):
    if lib not in _libs:
        _libs[lib] = sexp.parse(open(LIBDIR + lib + ".kicad_sym").read())
    for s in sexp.find(_libs[lib], "symbol"):
        if s[1] == name:
            if sexp.first(s, "extends"):
                raise ValueError(f"{lib}:{name} é derivado; use o símbolo base")
            out = list(s)
            out[1] = f"{lib}:{name}"
            return out
    raise KeyError(f"{lib}:{name}")


def pins_of(symdef):
    pins = {}

    def walk(n):
        for e in n:
            if isinstance(e, list) and e and e[0] == "pin":
                at = sexp.first(e, "at")
                pins[sexp.first(e, "number")[1]] = (float(at[1]), float(at[2]))
            elif isinstance(e, list):
                walk(e)
    walk(symdef)
    return pins


# --- símbolo próprio: SSR LOTI 48D25A (entrada DC 3+/4-, saída AC 1/2) --------------------
def ssr_symbol():
    S = lambda *a: [Sym(a[0]), *a[1:]]   # noqa: E731
    eff = lambda size=1.27, *extra: [Sym("effects"), [Sym("font"), [Sym("size"), size, size]], *extra]  # noqa: E731

    def pin(num, name, x, y, ang, typ="passive"):
        return [Sym("pin"), Sym(typ), Sym("line"), [Sym("at"), x, y, ang], [Sym("length"), 5.08],
                [Sym("name"), name, eff()], [Sym("number"), num, eff()]]

    def text(t, x, y, size=1.27):
        return [Sym("text"), t, [Sym("at"), x, y, 0], eff(size)]

    def prop(k, v, x, y, hide=False):
        e = eff()
        if hide:
            e.append(Sym("hide"))
        return [Sym("property"), k, v, [Sym("at"), x, y, 0], e]
    body = [Sym("symbol"), "SSR_LOTI_48D25A_0_1",
            [Sym("rectangle"), [Sym("start"), -7.62, 6.35], [Sym("end"), 7.62, -6.35],
             [Sym("stroke"), [Sym("width"), 0.254], [Sym("type"), Sym("default")]],
             [Sym("fill"), [Sym("type"), Sym("background")]]],
            [Sym("polyline"), [Sym("pts"), [Sym("xy"), 0, 6.35], [Sym("xy"), 0, -6.35]],
             [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("dash")]],
             [Sym("fill"), [Sym("type"), Sym("none")]]],
            text("DC", -3.81, 4.064, 1.0), text("5–32 V", -3.81, -4.318, 1.0),
            text("AC", 3.81, 4.064, 1.0), text("25 A", 3.81, -4.318, 1.0)]
    pins = [Sym("symbol"), "SSR_LOTI_48D25A_1_1",
            pin("3", "+", -12.7, 2.54, 0, "input"), pin("4", "−", -12.7, -2.54, 0, "input"),
            pin("1", "~", 12.7, 2.54, 180), pin("2", "~", 12.7, -2.54, 180)]
    return [Sym("symbol"), "Bancada:SSR_LOTI_48D25A", [Sym("pin_names"), [Sym("offset"), 1.016]],
            [Sym("in_bom"), Sym("yes")], [Sym("on_board"), Sym("yes")],
            prop("Reference", "K", 0, 8.89), prop("Value", "SSR_LOTI_48D25A", 0, -8.89),
            prop("Footprint", "", 0, 0, True), prop("Datasheet", "", 0, 0, True),
            body, pins]


# --- montagem do esquemático --------------------------------------------------------------
class Sch:
    def __init__(self):
        self.libs = {}
        self.items = []
        self.pwr = 0

    def use(self, lib_id):
        if lib_id not in self.libs:
            if lib_id == "Bancada:SSR_LOTI_48D25A":
                self.libs[lib_id] = ssr_symbol()
            else:
                lib, name = lib_id.split(":")
                self.libs[lib_id] = lib_symbol(lib, name)
        return self.libs[lib_id]

    def pin_xy(self, lib_id, at, num, rot=0):
        x, y = pins_of(self.use(lib_id))[num]
        a = math.radians(rot)
        xr = x * math.cos(a) - y * math.sin(a)
        yr = x * math.sin(a) + y * math.cos(a)
        return (round(at[0] + xr, 4), round(at[1] - yr, 4))

    @staticmethod
    def _eff(justify=None, hide=False, size=1.27):
        e = [Sym("effects"), [Sym("font"), [Sym("size"), size, size]]]
        if justify:
            e.append([Sym("justify"), *[Sym(j) for j in justify.split()]])
        if hide:
            e.append(Sym("hide"))
        return e

    def part(self, lib_id, ref, value, at, rot=0, ref_at=None, val_at=None, fields=None,
             ref_just="left", val_just="left", hide_ref=False):
        sd = self.use(lib_id)
        props = [
            [Sym("property"), "Reference", ref, [Sym("at"), *(ref_at or (at[0] + 2.54, at[1] - 1.27)), 0],
             self._eff(ref_just, hide_ref)],
            [Sym("property"), "Value", value, [Sym("at"), *(val_at or (at[0] + 2.54, at[1] + 1.27)), 0],
             self._eff(val_just)],
        ]
        for k, v in (fields or {}).items():
            props.append([Sym("property"), k, v, [Sym("at"), at[0], at[1], 0], self._eff(hide=True)])
        if not fields or "Footprint" not in fields:
            props.append([Sym("property"), "Footprint", "", [Sym("at"), at[0], at[1], 0], self._eff(hide=True)])
        if not fields or "Datasheet" not in fields:
            props.append([Sym("property"), "Datasheet", "", [Sym("at"), at[0], at[1], 0], self._eff(hide=True)])
        pins = [[Sym("pin"), n, [Sym("uuid"), str(uuid.uuid4())]] for n in pins_of(sd)]
        self.items.append([
            Sym("symbol"), [Sym("lib_id"), lib_id], [Sym("at"), at[0], at[1], rot], [Sym("unit"), 1],
            [Sym("in_bom"), Sym("no" if ref.startswith("#") else "yes")], [Sym("on_board"), Sym("yes")],
            [Sym("dnp"), Sym("no")], [Sym("uuid"), str(uuid.uuid4())], *props, *pins,
            [Sym("instances"), [Sym("project"), PROJECT,
                                [Sym("path"), f"/{ROOT}", [Sym("reference"), ref], [Sym("unit"), 1]]]]])

    def power(self, kind, at):
        self.pwr += 1
        name = {"GND": "power:GND", "+3V3": "power:+3V3"}[kind]
        off = 3.81 if kind == "GND" else -3.81
        self.part(name, f"#PWR0{self.pwr:02d}", kind, at, ref_at=(at[0], at[1] + off), hide_ref=True,
                  val_at=(at[0], at[1] + off * 1.35), val_just=None)

    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            self.items.append([Sym("wire"), [Sym("pts"), [Sym("xy"), *a], [Sym("xy"), *b]],
                               [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]],
                               [Sym("uuid"), str(uuid.uuid4())]])

    def junction(self, at):
        self.items.append([Sym("junction"), [Sym("at"), *at], [Sym("diameter"), 0],
                           [Sym("color"), 0, 0, 0, 0], [Sym("uuid"), str(uuid.uuid4())]])

    def label(self, name, at, left=False):
        self.items.append([Sym("label"), name, [Sym("at"), at[0], at[1], 180 if left else 0],
                           self._eff("right bottom" if left else "left bottom"),
                           [Sym("uuid"), str(uuid.uuid4())]])

    def nc(self, at):
        self.items.append([Sym("no_connect"), [Sym("at"), *at], [Sym("uuid"), str(uuid.uuid4())]])

    def text(self, t, at, size=1.27, bold=False):
        e = [Sym("effects"), [Sym("font"), [Sym("size"), size, size], *([Sym("bold")] if bold else [])],
             [Sym("justify"), Sym("left"), Sym("bottom")]]
        self.items.append([Sym("text"), t, [Sym("at"), at[0], at[1], 0], e, [Sym("uuid"), str(uuid.uuid4())]])

    def box(self, x0, y0, x1, y1):
        self.items.append([Sym("polyline"), [Sym("pts"), [Sym("xy"), x0, y0], [Sym("xy"), x1, y0],
                                             [Sym("xy"), x1, y1], [Sym("xy"), x0, y1], [Sym("xy"), x0, y0]],
                           [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("dash")]],
                           [Sym("uuid"), str(uuid.uuid4())]])

    def dump(self, title_block):
        doc = [Sym("kicad_sch"), [Sym("version"), Sym("20230121")], [Sym("generator"), Sym("eeschema")],
               [Sym("uuid"), ROOT], [Sym("paper"), "A4"], title_block,
               [Sym("lib_symbols"), *self.libs.values()], *self.items,
               [Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]]]
        return sexp.dump(doc) + "\n"


def build():
    s = Sch()
    R, NTC, C, HEAT = "Device:R", "Device:Thermistor_NTC", "Device:C", "Device:Heater"
    NANO, NPN, SSR, TERM = ("MCU_Module:Arduino_Nano_v2.x", "Transistor_BJT:BD911",
                            "Bancada:SSR_LOTI_48D25A", "Connector:Screw_Terminal_01x02")

    # ---- Arduino Nano 33 IoT ------------------------------------------------------------
    U = (55.88, 88.9)
    s.part(NANO, "U1", "Arduino Nano 33 IoT", U, ref_at=(30.48, 52.07), val_at=(30.48, 54.61),
           fields={"Footprint": "Module:Arduino_Nano",
                   "Datasheet": "https://docs.arduino.cc/hardware/nano-33-iot"})
    used = {"19", "20", "17", "4", "29", "30", "27"}
    for num in pins_of(s.use(NANO)):
        if num not in used:
            s.nc(s.pin_xy(NANO, U, num))
    a0, a1 = s.pin_xy(NANO, U, "19"), s.pin_xy(NANO, U, "20")
    s.wire(a0, (a0[0] + 7.62, a0[1])); s.label("NTC_ADC", (a0[0] + 7.62, a0[1]))
    s.wire(a1, (a1[0] + 7.62, a1[1])); s.label("SSR_CTRL", (a1[0] + 7.62, a1[1]))
    v33 = s.pin_xy(NANO, U, "17")
    s.power("+3V3", (v33[0], v33[1] - 5.08)); s.wire((v33[0], v33[1] - 5.08), v33)
    g1, g2 = s.pin_xy(NANO, U, "4"), s.pin_xy(NANO, U, "29")
    s.wire(g1, (g1[0], g1[1] + 5.08)); s.wire(g2, (g2[0], g2[1] + 5.08))
    s.wire((g1[0], g1[1] + 5.08), (g2[0], g2[1] + 5.08))
    s.junction((g1[0], g1[1] + 5.08)); s.power("GND", (g1[0], g1[1] + 7.62))
    s.wire((g1[0], g1[1] + 5.08), (g1[0], g1[1] + 7.62))
    vin, v5 = s.pin_xy(NANO, U, "30"), s.pin_xy(NANO, U, "27")
    s.nc(vin); s.nc(v5)
    s.text("Microcontrolador", (30.48, 30.48), 1.5, True)
    s.text("USB → PC (App: GET_DATA / SET_SP, 115 200 baud)", (30.48, 40.64))
    s.text("VIN e +5V: sem ligação vista nas fotos (ver V_SSR)", (30.48, 43.18), 1.0)
    s.text("Lógica de 3,3 V: os pinos não toleram 5 V", (30.48, 132.08), 1.0)

    # ---- Leitura do NTC (divisor ratiométrico em 3,3 V) --------------------------------
    x = 111.76
    s.text("Leitura de temperatura (A0)", (96.52, 30.48), 1.5, True)
    s.power("+3V3", (x, 40.64))
    s.part(R, "R1", "10k 1%", (x, 50.8))
    r1a, r1b = s.pin_xy(R, (x, 50.8), "1"), s.pin_xy(R, (x, 50.8), "2")
    s.wire((x, 40.64), r1a)
    node = (x, 62.23)
    s.wire(r1b, node); s.junction(node)
    s.wire((x - 7.62, node[1]), node); s.label("NTC_ADC", (x - 7.62, node[1]), left=True)
    s.part(NTC, "TH1", "NTC 10k β3950", (x, 72.39), ref_at=(x + 2.54, 71.12), val_at=(x + 2.54, 73.66))
    t1a, t1b = s.pin_xy(NTC, (x, 72.39), "1"), s.pin_xy(NTC, (x, 72.39), "2")
    s.wire(node, t1a); s.power("GND", (x, 82.55)); s.wire(t1b, (x, 82.55))
    s.text("(dentro do forno)", (x + 2.54, 76.2), 1.0)
    s.text("R_NTC = 10k · N / (4095 − N)", (96.52, 92.71), 1.0)
    s.text("1/T = 1/298,15 + ln(R_NTC/10k)/3950", (96.52, 95.25), 1.0)
    s.text("ADC 12 bits, média de 500 amostras", (96.52, 97.79), 1.0)

    # ---- Capacitor visto no breadboard (a confirmar) ------------------------------------
    cx = 152.4
    s.box(139.7, 27.94, 180.34, 86.36)
    s.text("A CONFIRMAR", (140.97, 31.75), 1.27, True)
    s.text("capacitor cerâmico no breadboard:", (140.97, 34.29), 1.0)
    s.text("valor e ligação não visíveis nas fotos", (140.97, 36.83), 1.0)
    s.power("+3V3", (cx, 50.8))
    s.part(C, "C1", "100n?", (cx, 60.96))
    c1a, c1b = s.pin_xy(C, (cx, 60.96), "1"), s.pin_xy(C, (cx, 60.96), "2")
    s.wire((cx, 50.8), c1a); s.power("GND", (cx, 72.39)); s.wire(c1b, (cx, 72.39))
    s.text("(provável desacoplamento)", (140.97, 83.82), 1.0)

    # ---- Acionamento do SSR (A1 → 1k → TIP31) -----------------------------------------
    y = 124.46
    s.text("Acionamento do SSR (A1)", (96.52, 109.22), 1.5, True)
    s.part(R, "R2", "1k", (111.76, y), rot=90, ref_at=(111.76, y - 3.81), val_at=(111.76, y + 3.81),
           ref_just=None, val_just=None)
    r2a, r2b = sorted([s.pin_xy(R, (111.76, y), "1", 90), s.pin_xy(R, (111.76, y), "2", 90)])
    s.wire((101.6, y), r2a); s.label("SSR_CTRL", (101.6, y), left=True)
    q = (129.54, y)
    s.part(NPN, "Q1", "TIP31 (1 B, 2 C, 3 E)", q, ref_at=(q[0] + 5.08, q[1] - 1.27),
           val_at=(q[0] + 5.08, q[1] + 1.27),
           fields={"Footprint": "Package_TO_SOT_THT:TO-220-3_Vertical"})
    qb, qc, qe = (s.pin_xy(NPN, q, n) for n in ("1", "2", "3"))
    s.wire(r2b, qb)
    s.wire(qe, (qe[0], qe[1] + 5.08)); s.power("GND", (qe[0], qe[1] + 5.08))
    s.text("A1 = HIGH (3,3 V): I_B ≈ (3,3 − 0,8)/1k ≈ 2,5 mA", (96.52, 147.32), 1.0)
    s.text("→ o TIP31 satura e puxa o −4 do SSR para GND", (96.52, 149.86), 1.0)

    k = (160.02, 111.76)
    s.part(SSR, "K1", "LOTI 48D25A", k, ref_at=(k[0], k[1] - 8.89), val_at=(k[0], k[1] + 10.16),
           ref_just=None, val_just=None)
    kp, kn, k1, k2 = (s.pin_xy(SSR, k, n) for n in ("3", "4", "1", "2"))
    s.wire(qc, (qc[0], kn[1]), kn)
    s.wire(kp, (kp[0] - 5.08, kp[1])); s.label("V_SSR", (kp[0] - 5.08, kp[1]), left=True)

    # alimentação do +3 do SSR (a confirmar)
    s.box(154.94, 134.62, 218.44, 162.56)
    s.text("A CONFIRMAR: de onde vem o +3 do SSR", (156.21, 138.43), 1.0, True)
    s.text("VIN/+5V do Nano (USB) ou a fonte chaveada;", (156.21, 140.97), 1.0)
    s.text("o GND tem de ser comum ao do Nano", (156.21, 143.51), 1.0)
    jx, jy = 180.34, 149.86
    s.part(TERM, "J2", "V_SSR 5–32 V", (jx, jy), ref_at=(jx + 2.54, jy - 1.27), val_at=(jx + 2.54, jy + 5.08))
    j1p, j2p = s.pin_xy(TERM, (jx, jy), "1"), s.pin_xy(TERM, (jx, jy), "2")
    s.wire(j1p, (j1p[0] - 5.08, j1p[1])); s.label("V_SSR", (j1p[0] - 5.08, j1p[1]), left=True)
    s.wire(j2p, (j2p[0] - 5.08, j2p[1]), (j2p[0] - 5.08, j2p[1] + 2.54))
    s.power("GND", (j2p[0] - 5.08, j2p[1] + 2.54))

    # ---- Lado AC: rede 220 V → SSR → resistência do forno --------------------------------
    s.text("Lado AC 220 V (perigo)", (185.42, 99.06), 1.5, True)
    term = (238.76, k1[1])
    s.part(TERM, "J1", "Rede 220 V (1 = L, 2 = N)", term, ref_at=(term[0] + 2.54, term[1] - 1.27),
           val_at=(term[0] + 2.54, term[1] + 5.08))
    l_pin, n_pin = s.pin_xy(TERM, term, "1"), s.pin_xy(TERM, term, "2")
    s.wire(k1, l_pin)
    hx = 203.2
    s.part(HEAT, "H1", "Resistência do forno", (hx, 121.92), ref_at=(hx + 2.54, 120.65),
           val_at=(hx + 2.54, 123.19))
    h1a, h1b = s.pin_xy(HEAT, (hx, 121.92), "1"), s.pin_xy(HEAT, (hx, 121.92), "2")
    s.wire(k2, (hx, k2[1]), h1a)
    s.wire(h1b, (hx, h1b[1] + 3.81), (231.14, h1b[1] + 3.81), (231.14, n_pin[1]), n_pin)
    s.text("Odontobras EL 1.1 (original)", (hx + 2.54, 125.73), 1.0)

    # ---- Notas ---------------------------------------------------------------------------
    nx, ny = 20.32, 167.64
    notes = [
        "Fontes: PID_Controller.ino (NTC_PIN = A0, SSR_PIN = A1 \"via TIP31\"), SSR_TEST.ino (A1 → 1k → base do TIP31),",
        "TCC 2026 (NTC 10 kΩ β 3950, R_div 10 kΩ 1 %, leitura ratiométrica em 3,3 V; SSR LOTI 48D25A zero-cross, carga 220 V)",
        "e fotos do breadboard de 29/10/2026. O TIP31 usa o símbolo BD911 da biblioteca (mesmo NPN TO-220, mesma pinagem).",
        "Controle: PID (Kp 2,78, Ki 0,00106, Kd 5,0) com janela de 5 s no SSR (time-proportioning).",
    ]
    for i, t in enumerate(notes):
        s.text(t, (nx, ny + i * 2.54), 1.0)

    tb = [Sym("title_block"), [Sym("title"), "Controle do forno PID"],
          [Sym("date"), "2026-10-29"], [Sym("rev"), "1"], [Sym("company"), "UFC / LESC — bancada de burn-in"],
          [Sym("comment"), 1, "Levantado do firmware, do TCC e das fotos; itens tracejados a confirmar"],
          [Sym("comment"), 2, "Arduino Nano 33 IoT + NTC 10k + TIP31 + SSR LOTI 48D25A"]]
    return s.dump(tb)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"{PROJECT}.kicad_sch"), "w") as f:
        f.write(build())
    with open(os.path.join(out, f"{PROJECT}.kicad_pro"), "w") as f:
        json.dump({"meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
                   "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
                   "sheets": [[ROOT, ""]]}, f, indent=2)
    print("ok", out)
