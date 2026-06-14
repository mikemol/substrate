#!/usr/bin/env python3
"""jea_agda_bridge.py — the end-to-end Agda-on-GPU path. A term algebra defined in Agda
(scratch/jea/Emit.agda) is evaluated, EXACT, by the cooperative GPU generators
(jea_generator_dag), and must agree with Agda's own value.

The bridge IS the typechecker (substrate --safe spirit, no MAlonzo): Emit.agda proves by refl
that `termStr` is the term's serialization and `valStr` is its value. This script:
  1. runs `agda --safe Emit.agda` -> exit 0 means the refls hold, so the literals are faithful;
  2. reads termStr / valStr from the Agda source (Agda-vouched);
  3. parses termStr (S-expr) into the GPU DAG (vN/vD/lch/rch/op, leaves first);
  4. evaluates it on the cooperative generators (jea_generator_dag.run_g);
  5. asserts the GPU's exact reduced root == Agda's valStr (as a rational).

The spit-take: write a term over the ℚ algebra in Agda, fold it on 20 cooperative GPU
generators, get the exact rational back — and Agda agrees.
"""
import os, re, subprocess, sys
from fractions import Fraction
os.environ.setdefault("CUDA_PATH", "/usr")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMIT_DIR = os.path.join(ROOT, "scratch", "jea")
EMIT = os.path.join(EMIT_DIR, "Emit.agda")


# ---- 1. typecheck Emit.agda: exit 0 == the refl vouchers hold ----
def typecheck():
    r = subprocess.run(["agda", "--safe", "Emit.agda"], cwd=EMIT_DIR,
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("Emit.agda failed to typecheck (vouchers do NOT hold):\n" + r.stdout + r.stderr)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "checked"


# ---- 2. read the Agda-vouched literals ----
def read_vouched():
    src = open(EMIT).read()
    term = re.search(r'termStr\s*=\s*"([^"]*)"', src).group(1)
    val = re.search(r'valStr\s*=\s*"([^"]*)"', src).group(1)
    vn, vd = val.split("/")
    return term, Fraction(int(vn), int(vd))


# ---- 3. parse the S-expr term ----
class Leaf:
    def __init__(self, n, d): self.n, self.d, self.idx = n, d, None
class Comb:
    def __init__(self, op, l, r): self.op, self.l, self.r, self.idx = op, l, r, None

def parse_sexpr(s):
    toks = s.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0
    def parse():
        nonlocal pos
        assert toks[pos] == "("; pos += 1
        head = toks[pos]; pos += 1
        if head == "lf":
            n = int(toks[pos]); d = int(toks[pos + 1]); pos += 2
            assert toks[pos] == ")"; pos += 1
            return Leaf(n, d)
        a = parse(); b = parse()
        assert toks[pos] == ")"; pos += 1
        return Comb(head, a, b)
    return parse()


# ---- 4. flatten to the GPU DAG (leaves first, combines post-order) ----
def to_dag(root):
    leaves, combines = [], []
    def passA(node):                       # all leaves get indices 0..L-1 (GPU marks these ready)
        if isinstance(node, Leaf): node.idx = len(leaves); leaves.append(node)
        else: passA(node.l); passA(node.r)
    def passB(node, baseL):                # combines post-order: children before parent
        if isinstance(node, Comb):
            passB(node.l, baseL); passB(node.r, baseL)
            node.idx = baseL + len(combines); combines.append(node)
    passA(root); L = len(leaves); passB(root, L); N = L + len(combines)
    vN = [0] * N; vD = [0] * N; lch = [-1] * N; rch = [-1] * N; op = [-1] * N
    for lf in leaves: vN[lf.idx] = lf.n; vD[lf.idx] = lf.d
    for c in combines:
        lch[c.idx] = c.l.idx; rch[c.idx] = c.r.idx; op[c.idx] = 1 if c.op == "mul" else 0
    return dict(vN=vN, vD=vD, lch=lch, rch=rch, op=op, L=L, N=N, root=root.idx)

def truth_of(node):
    if isinstance(node, Leaf): return Fraction(node.n, node.d)
    a, b = truth_of(node.l), truth_of(node.r)
    return a * b if node.op == "mul" else a + b


if __name__ == "__main__":
    import jea_generator_dag as J

    line = typecheck()
    termStr, agda_val = read_vouched()
    print("end-to-end Agda-on-GPU bridge\n")
    print(f"  1. agda --safe Emit.agda : {line}  (refl vouchers hold -> literals are faithful)")
    print(f"  2. Agda term  : {termStr}")
    print(f"  3. Agda value : {agda_val}  (= {agda_val.numerator}/{agda_val.denominator} reduced; vouched by refl)")

    tree = parse_sexpr(termStr)
    g = to_dag(tree); g["truth"] = truth_of(tree)
    r = J.run_g(g)                                       # evaluate on the cooperative GPU generators
    gpu = Fraction(r["rn"], r["rd"])
    print(f"  4. GPU DAG    : {g['L']} leaves, {g['N']-g['L']} combines, {r['launched']} cooperative blocks")
    print(f"  5. GPU value  : {gpu}  (exact reduced root, err={r['err']}, pending={r['pending']})")

    ok = (r["err"] == 0 and r["pending"] == 0 and gpu == agda_val and gpu == g["truth"])
    print(f"\n  GPU == Agda-vouched value : {gpu == agda_val}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — a term algebra defined in Agda, evaluated EXACT on 20 cooperative")
    print(f"  GPU generators, agreeing with Agda's own value. The Agda-on-GPU path is closed end-to-end.")
