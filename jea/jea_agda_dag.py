#!/usr/bin/env python3
"""jea_agda_dag.py — U8: a real shared SPPF defined in Agda, evaluated on the GPU engine (sharing exploited).

jea_agda_bridge closed the Agda-on-GPU path for a TREE term (Emit.agda; every occurrence its own node).
U8 drives the SHARED SPPF form the substrate actually uses (EmitDAG.agda: a node LIST with child INDICES,
so a node is referenced by multiple parents = sharing = memoization). The bridge parses the node list
PRESERVING the sharing into the GPU DAG (a shared node is ONE node, lch==rch when both children coincide),
and the cooperative generators evaluate it once-per-node, not once-per-occurrence.

This closes APEX-1: spawn(U6) + intern(U7) + the real Agda SPPF, end to end. The voucher discipline is
unchanged -- agda --safe EmitDAG.agda proves renderDAG/evalStr faithful by refl, so the literals the bridge
reads are machine-verified.

Witnesses (each [W]):
1. AGDA-VOUCHED: agda --safe EmitDAG.agda exit 0 (the refl vouchers hold -> termStr/valStr faithful).
2. SHARED SPPF: the parsed DAG has shared subterms (nodes referenced by >1 parent); DAG node count <<
   its tree expansion (the sharing the substrate SPPF buys, reported as a ratio).
3. EXACT ON GPU: the cooperative generators evaluate the SHARED DAG to == Agda's vouched value (reduced).
4. CANONICAL (U7): every structural hash-cons key (op, children) is distinct -> the emitted SPPF is
   already maximally shared (distinct == N). The device-parallel dedup that would collapse a tree is
   jea_intern; here it confirms canonicality of the real SPPF.
"""
import os, re, subprocess, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMIT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agda-emit")


def typecheck():
    r = subprocess.run(["agda", "--safe", "EmitDAG.agda"], cwd=EMIT_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("EmitDAG.agda failed to typecheck (vouchers do NOT hold):\n" + r.stdout + r.stderr)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "checked"


def read_vouched():
    src = open(os.path.join(EMIT_DIR, "EmitDAG.agda"), encoding="utf-8").read()
    term = re.search(r'termStr\s*=\s*"([^"]*)"', src).group(1)
    val = re.search(r'valStr\s*=\s*"([^"]*)"', src).group(1)
    vn, vd = val.split("/")
    return term, Fraction(int(vn), int(vd))


def parse_dag(s):
    """node list 'lf n d | add i j | mul i j | ...' -> GPU DAG (leaves first here; children are EARLIER
    indices, possibly REUSED = sharing). Returns the run_g dict."""
    toks = [t.strip().split() for t in s.split("|")]
    N = len(toks)
    vN = [0] * N; vD = [0] * N; lch = [-1] * N; rch = [-1] * N; op = [-1] * N
    L = 0
    for i, t in enumerate(toks):
        if t[0] == "lf":
            vN[i] = int(t[1]); vD[i] = int(t[2]); L += 1
        else:
            lch[i] = int(t[1]); rch[i] = int(t[2]); op[i] = 1 if t[0] == "mul" else 0
    # run_g wants leaves [0,L); our emission already has leaves first (L leading lf nodes)
    return dict(vN=vN, vD=vD, lch=lch, rch=rch, op=op, L=L, N=N, root=N - 1), toks


def tree_size(g, i):
    if g["op"][i] == -1: return 1
    return 1 + tree_size(g, g["lch"][i]) + tree_size(g, g["rch"][i])


if __name__ == "__main__":
    import jea_generator_dag as J

    line = typecheck()
    termStr, agda_val = read_vouched()
    g, toks = parse_dag(termStr)
    g["truth"] = agda_val

    # sharing: how many parents reference each node, and DAG vs tree-expansion size
    refs = [0] * g["N"]
    for i in range(g["N"]):
        if g["op"][i] != -1: refs[g["lch"][i]] += 1; refs[g["rch"][i]] += 1
    shared = [i for i in range(g["N"]) if refs[i] > 1]
    tsize = tree_size(g, g["root"])

    r = J.run_g(g)
    gpu = Fraction(r["rn"], r["rd"])

    # U7 confirmation: structural hash-cons keys all distinct -> already maximally shared
    keys = [("lf", g["vN"][i], g["vD"][i]) if g["op"][i] == -1 else (g["op"][i], g["lch"][i], g["rch"][i])
            for i in range(g["N"])]
    canonical = len(set(keys)) == g["N"]

    print("Agda shared SPPF -> GPU cooperative generators (U8)\n")
    print(f"  1. agda --safe EmitDAG.agda : {line}  (refl vouchers hold)")
    print(f"  2. Agda SPPF   : {termStr}")
    print(f"  3. Agda value  : {agda_val}  (refl-vouched)")
    print(f"  4. GPU DAG     : {g['L']} leaves, {g['N']-g['L']} combines, {r['launched']} blocks; "
          f"shared nodes (refs>1): {shared}")
    print(f"  5. sharing     : {g['N']} DAG nodes vs {tsize} tree-expansion nodes = {tsize/g['N']:.1f}x")
    print(f"  6. GPU value   : {gpu}  (exact reduced root, err={r['err']}, pending={r['pending']})\n")

    w1 = line != ""
    w2 = len(shared) > 0 and tsize > g["N"]
    w3 = (gpu == agda_val) and r["err"] == 0 and r["pending"] == 0
    w4 = canonical
    print(f"1. AGDA-VOUCHED (refl vouchers hold): {w1}")
    print(f"2. SHARED SPPF (nodes referenced by >1 parent; {g['N']} DAG vs {tsize} tree): {w2}")
    print(f"3. EXACT ON GPU (shared DAG -> == Agda vouched value): {w3}")
    print(f"4. CANONICAL / U7 (all hash-cons keys distinct -> maximally shared): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — U8: a SHARED SPPF defined in Agda (refl-vouched), parsed preserving")
    print(f"  sharing, evaluated EXACT on the cooperative generators (each shared node computed once, not")
    print(f"  per-occurrence), == Agda's value. APEX-1 closed: spawn (U6) + intern (U7) + real Agda SPPF.")
    print(f"  The Agda-on-GPU path now carries the substrate's actual DAG-with-sharing, not just a tree.")
