#!/usr/bin/env python3
"""jea_agda_voucher.py — the Agda voucher protocol, shared by the Agda-on-GPU bridges.

jea_agda_bridge (a TREE term, Emit.agda) and jea_agda_dag (a SHARED SPPF, EmitDAG.agda) both open
with the same two steps: typecheck an Agda voucher file under `agda --safe` (exit 0 == the refl
vouchers hold, so the emitted termStr/valStr literals are machine-faithful), then read those two
literals back. The ONLY thing that differed between the two copies was the voucher FILENAME — so the
filename is the parameter, and the body lives here once. Each bridge keeps a thin wrapper that binds
its own default filename (Emit.agda / EmitDAG.agda), preserving every existing no-arg caller.

Pure stdlib (no cupy, no GPU): this is the agda-subprocess + literal-read surface only. (The Λ8b
coupling-surface note "agda_bridge/agda_dag do the subprocess agda + the EMIT_DIR open" now points
here — same surface, one home; no scratch reference, so Λ8/Λ8b stay green.)
"""
import os, re, subprocess, sys
from fractions import Fraction

EMIT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agda-emit")


def typecheck(name):
    """`agda --safe <name>` in the emit dir; sys.exit if the vouchers fail (refls do NOT hold);
    return the last stdout line (or 'checked' when agda is silent)."""
    r = subprocess.run(["agda", "--safe", name], cwd=EMIT_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(name + " failed to typecheck (vouchers do NOT hold):\n" + r.stdout + r.stderr)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "checked"


def read_vouched(name):
    """read the refl-vouched literals from the emit file: termStr (the serialization) and valStr
    (its value as n/d), the latter returned as an EXACT Fraction."""
    src = open(os.path.join(EMIT_DIR, name), encoding="utf-8").read()
    term = re.search(r'termStr\s*=\s*"([^"]*)"', src).group(1)
    val = re.search(r'valStr\s*=\s*"([^"]*)"', src).group(1)
    vn, vd = val.split("/")
    return term, Fraction(int(vn), int(vd))
