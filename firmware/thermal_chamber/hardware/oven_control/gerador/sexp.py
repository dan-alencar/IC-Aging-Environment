"""S-expression mínimo para ler/escrever arquivos do KiCad."""
import re

class Sym(str):
    """Átomo sem aspas (palavra-chave ou número)."""

TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')

def parse(text):
    stack, cur = [], []
    pos = 0
    while True:
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        if m.group(1):
            stack.append(cur); cur = []
        elif m.group(2):
            done = cur; cur = stack.pop(); cur.append(done)
        elif m.group(3) is not None:
            cur.append(m.group(3).replace('\\"', '"').replace("\\\\", "\\"))
        else:
            cur.append(Sym(m.group(4)))
    return cur[0] if len(cur) == 1 else cur

def dump(x, ind=0):
    sp = "  " * ind
    if isinstance(x, list):
        simple = all(not isinstance(e, list) for e in x)
        if simple:
            return sp + "(" + " ".join(atom(e) for e in x) + ")"
        head = []
        rest = []
        for e in x:
            (rest if isinstance(e, list) or rest else head).append(e)
        out = sp + "(" + " ".join(atom(e) for e in head)
        for e in rest:
            out += "\n" + (dump(e, ind + 1) if isinstance(e, list) else "  " * (ind + 1) + atom(e))
        return out + ")"
    return sp + atom(x)

def atom(e):
    if isinstance(e, Sym):
        return str(e)
    if isinstance(e, (int, float)):
        return fmt_num(e)
    return '"' + str(e).replace("\\", "\\\\").replace('"', '\\"') + '"'

def fmt_num(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def find(lst, key):
    return [e for e in lst if isinstance(e, list) and e and e[0] == key]

def first(lst, key):
    r = find(lst, key)
    return r[0] if r else None
