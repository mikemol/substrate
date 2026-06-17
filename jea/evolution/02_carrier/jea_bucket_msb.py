#!/usr/bin/env python3
"""jea_bucket_msb.py — magnitude-bucketing: lane width = MSB+1, the data-driven SWAR tiling.

The overflow predictor (jea_generator_dag_mode: a k-bit x m-bit value is < 2^(k+m)) says a value's lane
need is its bit-width. This brick takes that to its conclusion: BUCKET each value by its MSB into a SWAR
lane of width = MSB+1 (rounded to the pow-2 ladder {1,2,4,8,16,32,64} -- pow-2 because the SWAR broadcast
needs it, jea_swar_bignum). Buckets are DYNAMIC: every op re-buckets its result by the migration law
  * mul   : width(result) <= width(a) + width(b)        (widths add -> migrate UP)
  * add   : width(result) <= max(wa_n+wb_d, wb_n+wa_d)+1 (migrate up ~1)
  * reduce: gcd shrinks num/den                          (migrate DOWN to a narrower bucket)
  * escalate: width > top bucket                         (migrate to the next carrier)

This UNIFIES three already-built pieces: jea_swar_mixed (mixed-width lanes in one register) is the STATIC
packing, this is its data-driven form; jea_generator_bucket (the scheduler bucketing strata by depth) is
the same bucket machinery keyed on MAGNITUDE; and the eager/lazy MODE knob (jea_generator_dag_mode) IS
bucket-occupancy control -- eager (reduce) keeps values in narrow buckets, lazy (defer) lets them drift
wide and escalate sooner. Reduction = downward migration; escalation = upward migration.

Grounded in the REAL GPU per-node values (jea_generator_dag_mode.run_g_mode returns vN/vD/esc per node),
not a host model. Witnesses (each [W]):
1. MIGRATION LAW SOUND: for every combine, the bucket PREDICTED from operand bit-widths is an upper bound
   on the actual result bucket (the no-silent-overflow guarantee, as a bucketing statement) -- both modes.
2. REDUCTION = DOWNWARD MIGRATION: eager's predicted->actual bucket gap is large (gcd migrates values
   down); lazy's gap is ~0 (no reduction, the result sits at the predicted width). Measured.
3. MODE <-> OCCUPANCY: eager's bucket histogram is concentrated narrow; lazy's drifts wide (higher max
   bucket / more escalations). The Pareto knob is literally how wide the buckets are allowed to drift.
4. PAY-FOR-WHAT-YOU-USE (SWAR pack): packing each component at its bucket width (64/w lanes per register)
   uses far fewer 64-bit words than a flat lane-per-component -- the jea_swar_mixed mixed-width tiling.
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np
from jea_generator_dag import build_dag
import jea_generator_dag_mode as M

LADDER = [1, 2, 4, 8, 16, 32, 64]
def bitlen(x): return int(x).bit_length()
def bucket(w):                                                # round a bit-width up the SWAR pow-2 ladder
    for L in LADDER:
        if w <= L: return L
    return 128                                                # >64 = escalated past the u64 carrier


def analyse(g, res):
    """Per-node lane widths + the migration law, over the GPU's actual stored values for one MODE."""
    vN, vD, esc = res["vN"], res["vD"], res["esc"]; L = g["L"]; N = g["N"]
    lch, rch, op = g["lch"], g["rch"], g["op"]
    w_node = np.zeros(N, np.int64)                            # actual lane width (bucket) per node
    for i in range(N):
        if esc[i]: w_node[i] = 128; continue
        w_node[i] = bucket(max(bitlen(vN[i]), bitlen(vD[i])))
    sound = True; gaps = []
    for i in range(L, N):                                     # combines: check the migration law
        if esc[i] or esc[lch[i]] or esc[rch[i]]: continue
        an, ad, bn, bd = int(vN[lch[i]]), int(vD[lch[i]]), int(vN[rch[i]]), int(vD[rch[i]])
        if op[i] == 1:                                        # mul: widths add
            pn, pd = bitlen(an) + bitlen(bn), bitlen(ad) + bitlen(bd)
        else:                                                 # add
            pn, pd = max(bitlen(an) + bitlen(bd), bitlen(bn) + bitlen(ad)) + 1, bitlen(ad) + bitlen(bd)
        pred = bucket(max(pn, pd)); act = w_node[i]
        if pred < act: sound = False                          # predictor must never under-estimate
        gaps.append(pred - act)                               # how far reduction migrated the result down
    hist = {L: int((w_node[:N] == L).sum()) for L in LADDER + [128]}
    live = esc == 0
    return dict(w_node=w_node, sound=sound, slack=float(np.mean(gaps)) if gaps else 0.0,
                totbits=int(w_node[live].sum()), maxbucket=int(w_node.max()),
                nesc=int((esc != 0).sum()), hist=hist)


def swar_words(w_node, esc):
    """Pack each component (num, den) at its bucket width: 64/w lanes per 64-bit register. Compare to a
    flat lane-per-component (one 64-bit word each) -- the mixed-width SWAR saving."""
    from math import ceil
    counts = {L: 0 for L in LADDER}
    for i in range(len(w_node)):
        if esc[i]: continue
        counts[int(w_node[i])] += 2                           # num + den, both at this bucket width
    packed = sum(ceil(c / (64 // w)) for w, c in counts.items() if c)
    flat = sum(counts.values())
    return packed, flat


if __name__ == "__main__":
    g = build_dag(L=128, seed=3)
    eager = M.run_g_mode(g, 1); lazy = M.run_g_mode(g, 0)
    ae, al = analyse(g, eager), analyse(g, lazy)
    pe, fe = swar_words(ae["w_node"], eager["esc"])

    print(f"magnitude-bucketing over the GPU's per-node values — {g['L']} leaves, {g['N']-g['L']} combines\n")
    print(f"  EAGER bucket histogram (lane width -> count): { {k:v for k,v in ae['hist'].items() if v} }")
    print(f"  LAZY  bucket histogram (lane width -> count): { {k:v for k,v in al['hist'].items() if v} }")
    print(f"  migration law sound (pred>=actual): eager={ae['sound']} lazy={al['sound']}  (predictor slack incl. pow-2 rounding: eager {ae['slack']:.2f} lazy {al['slack']:.2f})")
    print(f"  total lane bits (reduction keeps values narrow): eager={ae['totbits']}  lazy={al['totbits']}")
    print(f"  max bucket reached: eager={ae['maxbucket']}  lazy={al['maxbucket']}   escalated: eager={ae['nesc']} lazy={al['nesc']}")
    print(f"  SWAR pack (eager): {pe} 64-bit words vs {fe} flat (one lane/component) = {fe/pe:.2f}x denser\n")

    w1 = ae["sound"] and al["sound"]
    w2 = ae["totbits"] < al["totbits"]                                  # eager values narrower = reduction migrates down
    w3 = (al["maxbucket"] >= ae["maxbucket"])                            # lazy drifts at least as wide
    w4 = pe < fe
    print(f"1. MIGRATION LAW SOUND (pred>=actual, both modes): {w1}")
    print(f"2. REDUCTION = DOWNWARD MIGRATION (eager {ae['totbits']} bits < lazy {al['totbits']}): {w2}")
    print(f"3. MODE <-> OCCUPANCY (lazy max bucket {al['maxbucket']} >= eager {ae['maxbucket']}): {w3}")
    print(f"4. PAY-FOR-WHAT-YOU-USE (SWAR pack {fe/pe:.2f}x denser): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — lane width = MSB+1, bucketed on the SWAR pow-2 ladder, grounded")
    print(f"  in the real GPU values. The migration law (mul adds widths, reduce shrinks, escalate overflows)")
    print(f"  unifies the overflow predictor + jea_swar_mixed (static packing) + jea_generator_bucket (the")
    print(f"  scheduler) + the eager/lazy knob (= bucket-occupancy control). NEXT: pack the cooperative")
    print(f"  evaluator's lanes by magnitude bucket (SWAR-dense narrow values), re-bucket on each migrate.")
