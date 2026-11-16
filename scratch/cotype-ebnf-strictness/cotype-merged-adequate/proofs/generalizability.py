#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Generalizability-mapper: the DUAL of corruption-testing.

Corruption asks "is this step load-bearing?" (break it, watch it go red). This asks the dual:
"over what RANGE does the conclusion hold, and how much structure is inessential to it?"

Method: lift a lemma's PINNED constants to free axes; sweep each axis; fit the closed form; report
(a) the survival range per axis, (b) which structure is GLOBAL to the family vs LOCAL to the pinned
corner. A pinned constant whose lift still fits a clean closed form was INESSENTIAL (quotientable);
one whose lift breaks the form was LOAD-BEARING (the result genuinely depends on it).

Worked instance: f090_2's nullity, pinned at c=2. Lifting c reveals nullity(p,c)=(c-1)(p-1)(cp-p-1)/2,
of which the (p-1)/2 'halving' is GLOBAL (survives all c) but the value (p-1)/2 is the c=2 corner.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'witnesses'))
import species_np as snp, numpy as np, sympy as sp

def build_cycles(sizes):
    """disjoint cycles of the given sizes (the n-pathness axis: len(sizes)=c, the values=block sizes)."""
    nv = sum(sizes); perm = list(range(nv)); off = 0
    for s in sizes:
        for i in range(s): perm[off+i] = off + ((i+1) % s)
        off += s
    return tuple(perm), nv

def phi_nullity(perm, nv, p):
    e, ei, C, Cp = snp.cyc_setup(nv); T = snp.rep(perm, e, ei, C, Cp).astype(complex)
    d = p-1; pw = [np.eye(T.shape[0], dtype=complex)]
    for _ in range(d): pw.append(pw[-1] @ T)
    M = sum(pw[d-i] for i in range(d+1))
    return M.shape[0] - np.linalg.matrix_rank(M, tol=1e-6)

# The generalized lemma found by lifting the c=2 pin (validated on held-out p=11, c≤7):
p, c = sp.symbols('p c')
NULLITY_PC = (c-1)*(p-1)*(c*p - p - 1)/2

def verify_closed_form(points):
    """Each point (pv,cv): does the closed form predict the actual nullity? Returns list of (pt,pred,act,ok)."""
    out = []
    for (pv, cv) in points:
        perm, nv = build_cycles([pv]*cv)
        act = phi_nullity(perm, nv, pv)
        pred = int(NULLITY_PC.subs({p: pv, c: cv}))
        out.append(((pv, cv), pred, act, pred == act))
    return out

def generalizability_report():
    # held-out validation (none of these were in the original c≤5,p≤7 fit)
    held = [(3, 6), (5, 6), (11, 2), (11, 3), (3, 7), (13, 2)]
    res = verify_closed_form(held)
    # structural decomposition: what's global vs the c=2 corner
    c2 = sp.factor(NULLITY_PC.subs(c, 2))
    mult = sp.factor(sp.simplify(NULLITY_PC/(p-1)))
    return {
        "closed_form_nullity": sp.factor(NULLITY_PC),
        "held_out": res,
        "all_held_pass": all(ok for *_, ok in res),
        "c2_slice": c2,                       # (p-1)²/2 — the original pinned result
        "mult_general": mult,                 # (c-1)(cp-p-1)/2 — n-pathness mult, the generalization
        "global_structure": "(p-1) factor and /2 survive ALL c (family-global)",
        "local_corner": "mult=(p-1)/2 is the c=2 slice ONLY; general mult=(c-1)(cp-p-1)/2 grows super-C(c,2)",
    }

if __name__ == "__main__":
    r = generalizability_report()
    print("GENERALIZABILITY MAP for f090_2's nullity (c=2 pin lifted to the n-pathness axis c):\n")
    print(f"  closed form (validated): nullity(p,c) = {r['closed_form_nullity']}")
    print(f"  held-out checks (p,c not in fit): {'ALL PASS' if r['all_held_pass'] else 'FAIL'}")
    for pt, pred, act, ok in r["held_out"]:
        print(f"      {pt}: pred {pred} = act {act}  {'✓' if ok else '✗'}")
    print(f"\n  c=2 slice recovers the pinned lemma: nullity(p,2) = {r['c2_slice']}  [= (p-1)²/2]")
    print(f"  general multiplicity: mult(p,c) = {r['mult_general']}")
    print(f"\n  GLOBAL (quotientable up to ∀c): {r['global_structure']}")
    print(f"  LOCAL (c=2 corner, load-bearing): {r['local_corner']}")
