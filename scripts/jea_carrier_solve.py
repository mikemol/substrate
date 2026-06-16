#!/usr/bin/env python3
"""jea_carrier_solve.py — Δ-Ω-carrier-slide: the carrier WIDTH is the OUTPUT of a live solve over bit-length,
not a baked u128. Slides DOWN to the narrowest carrier that holds the term, UP to byte-limb when it overflows.

THE FINDING (surfaced by the user via Δ-Φ): the apex (jea_apex / run_apex_u128) is u128-RESIDENT -- it launches
at 128 bits and stays. It escalates UP to byte-limb on overflow (err=2), but never slides DOWN: a 3-bit value
like 7/40 pays full u128 width. The carrier width was a FROZEN COORDINATE (128). The operative law
(coordinate->geometry, pay-for-what-you-use) says it must be a SURFACE: the value's predicted bit-length is the
geometry; place the term on the NARROWEST carrier that holds it, escalate only as magnitude demands.

THE FIX (reuse, don't reinvent -- the carriers already exist, the slide was just never wired):
  predict-place (a live O(N) solve over the DAG: propagate num/den bit-length upper bounds through the combines)
  -> pick the narrowest tier whose bound it fits:
      W <= 64   -> u64   carrier (jea_generator_dag.run_g, the cooperative generators)
      W <= 128  -> u128  carrier (jea_apex_deliver.run_apex_u128, the apex)
      W >  128  -> byte-limb     (jea_apex_deliver.deliver_bytelimb, escalate-don't-truncate, ANY magnitude)
The carrier is the OUTPUT of the solve, degenerating to the cheapest tier present -- never a baked 128.

Witnesses (each [W]):
1. SLIDE DOWN: a small term (7/40, ~7 bits) is placed on u64 -- NOT u128. The solve outputs the narrow carrier;
   pay-for-what-you-use restored (the apex's frozen u128 floor is gone).
2. SLIDE UP: a mid term (~124 bits) -> u128; a big term (217 bits) -> byte-limb. The SAME solve outputs each
   tier from the predicted bit-length -- the carrier tracks need, both directions.
3. EXACT EVERYWHERE + EXISTING CARRIERS: every tier returns the EXACT rational (== host truth); the dispatch
   reuses the three existing evaluators (u64 generators / u128 apex / byte-limb), no reinvention, no fit-to-carrier.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_apex_deliver import run_apex_u128, deliver_subtree, predict_per_node
import jea_generator_dag as G


def predict_width(g):
    """W = the binding max of the per-node bit-length upper bounds (predict_per_node, homed in jea_apex_deliver --
    the SAME formula the apex predict-places with). Mirrors the apex's in-kernel bln/bld; host-side for the SELECT."""
    nb, db = predict_per_node(g)
    return max(max(nb[i], db[i]) for i in range(g["N"]))


def carrier_solve(g):
    """The carrier as a live solve: predict the width, dispatch to the NARROWEST sufficient existing carrier. On
    escalation the byte-limb deliver solves over the escalation CROWN only (deliver_subtree), reusing the apex's
    correct u128 values for the rest -- not a whole-DAG recompute."""
    W = predict_width(g)
    if W <= 64:
        r = G.run_g(g); return Fraction(int(r["rn"]), int(r["rd"])), "u64", W
    val, err, nodes = run_apex_u128(g, return_nodes=True)
    if err != 2 and W <= 128:
        return val, "u128", W
    sub, _muls = deliver_subtree(g, nodes["vN"], nodes["vD"], escal=nodes["escal"])  # CROWN-only, crown = DEVICE residue
    return sub, "byte-limb", W


def _chain(primes):                                          # a mul-chain term in the lf/mul algebra (leaves-first DAG)
    N = len(primes); vN = list(primes) + [0]*(N-1); vD = [1]*N + [1]*(N-1)
    op = [-1]*N + [1]*(N-1); lch = [-1]*N + [0]*(N-1); rch = [-1]*N + [0]*(N-1)
    # right-fold: node N+k combines leaf k with the running product (leaf 0 .. or prior combine)
    prev = 0
    for k in range(1, N):
        idx = N + k - 1; lch[idx] = k; rch[idx] = prev; prev = idx
    g = dict(vN=vN, vD=vD, op=op, lch=lch, rch=rch, L=N, N=len(vN), root=len(vN)-1)
    truth = Fraction(1)
    for p in primes: truth *= p
    g["truth"] = truth
    return g


if __name__ == "__main__":
    print("Δ-Ω-carrier-slide: the carrier WIDTH is a live solve over bit-length -- slides DOWN and UP to need\n")
    P = [2000000011, 2000000033, 2000000063, 2000000087, 2000000089, 2000000099, 2000000147]
    small = _chain([2, 3]); small["truth"] = Fraction(6)     # 6 -> ~3 bits
    mid   = _chain(P[:4])                                    # 4 primes -> ~124 bits
    big   = _chain(P)                                        # 7 primes -> 217 bits
    rows = []
    for name, g in [("small (6, ~3b)", small), ("mid (4 primes)", mid), ("big (7 primes)", big)]:
        val, carrier, W = carrier_solve(g)
        ok = (val == g["truth"])
        rows.append((name, carrier, W, ok))
        print(f"  {name:<16} predicted W={W:>3} bits  ->  carrier {carrier:<10}  exact={ok}")

    carriers = [c for _, c, _, _ in rows]
    w1 = carriers[0] == "u64"                                # small slides DOWN off the u128 floor
    w2 = carriers[1] == "u128" and carriers[2] == "byte-limb"  # mid/big slide UP, by need
    w3 = all(ok for *_, ok in rows) and len(set(carriers)) == 3  # all exact, three distinct tiers from one solve
    print(f"\nW1 SLIDE DOWN (small term -> u64, OFF the baked u128 floor; pay-for-what-you-use): {w1}")
    print(f"W2 SLIDE UP (mid -> u128, big -> byte-limb; the same solve outputs each tier by predicted bits): {w2}")
    print(f"W3 EXACT EVERYWHERE + 3 DISTINCT TIERS from ONE live solve (existing carriers, no reinvention): {w3}")
    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the carrier WIDTH is now the OUTPUT of a live solve over the predicted")
    print(f"  bit-length geometry: u64 / u128 / byte-limb selected by NEED, sliding both directions. The apex's")
    print(f"  frozen u128 floor (launch-at-128-and-stay) is dissolved -- a small term pays u64, a huge one escalates")
    print(f"  to byte-limb, the SAME selector. Pay-for-what-you-use restored. NEXT rung (the full geometry): PER-NODE")
    print(f"  carrier placement (each node its narrowest), folding the predict-place into the on-GPU kernel dispatch")
    print(f"  (the host O(N) prediction here mirrors the apex's in-kernel bln/bld) -- carrier as a per-node surface.")
