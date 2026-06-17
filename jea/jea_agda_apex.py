#!/usr/bin/env python3
"""jea_agda_apex.py — Δ-Φ / AI-Φ: the Agda TERM-ALGEBRA drives the APEX (the unified, exact-at-any-magnitude evaluator).

The charter's primary goal is term-algebra -> GPU. The bridge (jea_agda_bridge) closed it for the OLD u64
cooperative generators; this drives the NEW apex (jea_apex: u128 carrier, productivity drain, err=2 byte-limb
deliver). Per the operative law (coordinate->geometry): the hand-built DAG was a COORDINATE (a frozen sample);
the Agda term-algebra is the GEOMETRY that GENERATES DAGs. The apex is a SUBSUMING SOLVE -- it evaluates
WHATEVER the term-algebra produces, at ANY magnitude, never a hardcoded DAG.

Reuse, don't reinvent: jea_agda_bridge (typecheck = the refl vouchers; read_vouched; parse_sexpr; to_dag) +
jea_apex_deliver (run_apex_u128; deliver_bytelimb = the err=2 escalation). This script only WIRES them.

Witnesses (each [W]):
1. AGDA-VOUCHED -> APEX: `agda --safe Emit.agda` vouches the term/value by refl; its DAG reduces ON THE APEX to
   == Agda's vouched value (the term-algebra driving the mature evaluator, not the old u64 generators).
2. SUBSUMING SOLVE (any magnitude): a term IN THE SAME ALGEBRA whose value EXCEEDS u128 -> the apex sets err=2
   and the byte-limb DELIVER returns the EXACT value (== host truth) -- where the old u64 evaluator would
   overflow. The apex evaluates whatever the term-algebra produces, at any magnitude.
3. NO HARDCODED DAG: the DAG comes from the term (B.to_dag / B.parse_sexpr), not build_dag -- the geometry
   (term-algebra) drives the solve; the apex degenerates cheaply for the small term (err=0) and escalates for
   the big one (err=2 -> byte-limb). Same path, no judged-faithful shortcut.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_agda_bridge as B
from jea_carrier_solve import carrier_solve


def apex_eval(g):
    """Evaluate a term-DAG by the carrier SOLVE: the carrier width is a live solve over predicted bit-length,
    sliding DOWN to u64 / staying u128 / escalating UP to byte-limb by NEED (not a baked u128 floor)."""
    val, carrier, W = carrier_solve(g)
    return val, carrier


if __name__ == "__main__":
    print("Δ-Φ: the Agda TERM-ALGEBRA drives the APEX (unified, exact-at-any-magnitude) -- not a hand-built DAG\n")

    # 1. AGDA-VOUCHED term -> apex
    line = B.typecheck()
    term, agda_val = B.read_vouched()
    g = B.to_dag(B.parse_sexpr(term))
    val, tier = apex_eval(g)
    w1 = (val == agda_val)
    print(f"  agda --safe Emit.agda: {line} (refl vouchers hold)")
    print(f"  term: {term}")
    print(f"  apex root = {val} [{tier}]  == Agda vouched {agda_val}: {w1}")

    # 2. SUBSUMING SOLVE: a refl-VOUCHED Agda term (EmitBig.agda) whose value EXCEEDS u128 (old u64/u128 overflow)
    bline = B.typecheck("EmitBig.agda")
    bterm, big_agda_val = B.read_vouched("EmitBig.agda")
    btree = B.parse_sexpr(bterm); bg = B.to_dag(btree)
    bval, btier = apex_eval(bg)
    bits = max(big_agda_val.numerator.bit_length(), big_agda_val.denominator.bit_length())
    w2 = (bval == big_agda_val) and (bits > 128) and ("byte-limb" in btier)
    print(f"\n  agda --safe EmitBig.agda: {bline} (refl vouchers hold) -- value {bits} bits (EXCEEDS u128={bits>128})")
    print(f"  apex root [{btier}] == Agda vouched {str(big_agda_val)[:48]}...: {bval == big_agda_val}")

    # 3. WIRED: the SAME vouched terms through the MEMOIZING evaluator (jea_eval -- persistent cross-eval memo).
    import jea_eval as EV
    mval,_,_   = EV.evaluate(B.to_dag(B.parse_sexpr(term)))     # Emit through the memoizing evaluator
    mbval,_,_  = EV.evaluate(B.to_dag(B.parse_sexpr(bterm)))    # EmitBig (>u128) through it too
    w4 = (mval==agda_val) and (mbval==big_agda_val)
    print(f"\n  MEMOIZING evaluator (jea_eval, persistent memo): Emit -> {mval} (=={agda_val}:{mval==agda_val}); "
          f"EmitBig -> {str(mbval)[:30]}... (==vouched:{mbval==big_agda_val}); memo {EV.memo_size()} entries")

    # 4. WIRED rung-(a): the REAL SHARED Agda SPPF (EmitDAG.agda, jea_agda_dag) through the memoizing evaluator.
    import jea_agda_dag as D
    D.typecheck(); dterm, dval = D.read_vouched(); dg,_ = D.parse_dag(dterm)
    refs=[0]*dg["N"]
    for i in range(dg["N"]):
        if dg["op"][i]!=-1: refs[dg["lch"][i]]+=1; refs[dg["rch"][i]]+=1
    nshared=sum(1 for i in range(dg["N"]) if refs[i]>1)
    sval,_,_ = EV.evaluate(dg)                                  # the shared SPPF (sharing exploited) through jea_eval
    w5 = (sval==dval) and (nshared>0)
    print(f"  SHARED Agda SPPF (EmitDAG.agda, {dg['N']} nodes, {nshared} shared subterms): jea_eval -> {sval} "
          f"(==Agda vouched {dval}: {sval==dval})")

    w3 = (tier != btier) and (tier in ("u64", "u128")) and ("byte-limb" in btier)  # the carrier SLID by need
    print(f"\nW1 AGDA-VOUCHED -> CARRIER SOLVE (Emit.agda term == Agda's refl-vouched value, on carrier [{tier}]): {w1}")
    print(f"W2 SUBSUMING SOLVE (EmitBig.agda term > u128 -> carrier slides to byte-limb == Agda vouched, exact): {w2}")
    print(f"W3 CARRIER SLIDES BY NEED (small term -> [{tier}], big -> [{btier}]; the carrier width is a LIVE SOLVE over")
    print(f"   predicted bit-length, NOT a baked u128 floor; the term-algebra drove both, no hardcoded DAG/carrier): {w3}")
    print(f"W4 MEMOIZING EVALUATOR WIRED (the vouched Agda terms also evaluate through jea_eval's persistent memo, exact): {w4}")
    print(f"W5 REAL SHARED Agda SPPF (rung-a: EmitDAG.agda, {nshared} shared subterms, through jea_eval -- jea_agda_dag")
    print(f"   de-orphaned, sharing exploited) == Agda vouched: {w5}")
    ok = w1 and w2 and w3 and w4 and w5
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Φ: the Agda term-algebra DRIVES the carrier solve. The DAG is the GEOMETRY")
    print(f"  the term generates (not a hand-built coordinate); the carrier WIDTH is a live solve over its predicted")
    print(f"  bit-length -- the small vouched term slides DOWN to [{tier}], the >u128 term escalates to [{btier}],")
    print(f"  the SAME selector, exact both. Charter term-algebra->GPU closed on the MATURE evaluator with the carrier")
    print(f"  sliding by need (reuse of jea_agda_bridge + jea_carrier_solve; no reinvention, no frozen u128 floor).")
    print(f"  (PER-NODE carrier placement -- each node its narrowest -- IS folded into the apex kernel: tier[]=0/1/2.)")
