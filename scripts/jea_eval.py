#!/usr/bin/env python3
"""jea_eval.py — the MEMOIZING evaluator: terms are INTERNED + SHARED into a PERSISTENT DEVICE-RESIDENT SPPF
forest (jea_resident, Δ-Σ-trace b-real); only genuinely-NEW nodes are evaluated. (You don't prune an SPPF -- you
share into it; the forest grows monotonically.) This module is the public eval entry + the supervisor DECISION WAL.

The resident forest now lives ON-DEVICE (jea_resident.Forest: a cupy sorted z-code index = a linear quadtree;
sharing-lookup is cp.searchsorted, growth is a device merge). evaluate(g) delegates to it: intern the term into
the resident forest, evaluate ONLY the new frontier on the apex, return the root value. A stream of overlapping
terms evaluates each distinct sub-term ONCE, ever. recompute-from-residue [[feedback_never_discard_residue]].

The DECISION WAL is held HERE too -- the THREE traces are one structure: eval-SPPF (the resident forest),
gcd/EEA residue (the reduced/CF value), and the supervisor decision WAL (evidence -> operating-point). The WAL is
the ordered EEA trace; _DMEMO is its interned form (recurring evidence = ONE node, like the forest interns subterms).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_resident as R                                       # the DEVICE-RESIDENT forest (b-real); module-import light

_FOREST = R.Forest()                                           # the persistent on-device SPPF, shared across all evaluate() calls

def evaluate(g):
    """Intern g into the persistent DEVICE-RESIDENT forest and evaluate only the new frontier; existing sub-terms
    are SHARED (referenced via the device searchsorted), never recomputed. Returns (value, evaluated_new, shared)."""
    return R.evaluate(g, _FOREST)

def memo_size(): return _FOREST.size()                         # resident SPPF size (distinct sub-terms ever seen)

# --- the SUPERVISOR DECISION WAL, held HERE (same module as the eval forest) as ONE trace structure (Δ-Σ-trace c) ---
_DMEMO = {}   # evidence key -> operating-point (the interned distinct decisions = SPPF of the control loop)
_WAL   = []   # ordered (evidence-key, op, was_hit) -- the never-discard residue of the control loop

def record_decision(evkey, op):
    """Fold one supervisor decision into the WAL/memo. Returns (was_hit, canonical_op). Recurring evidence HITS
    the memo -> the cached decision is reused (the supervisor need not re-derive), and the trace interns it."""
    hit = evkey in _DMEMO
    if not hit: _DMEMO[evkey] = op
    _WAL.append((evkey, op, hit))
    return hit, _DMEMO[evkey]

def wal_len(): return len(_WAL)
def distinct_decisions(): return len(_DMEMO)


if __name__ == "__main__":
    print("jea_eval: memoizing evaluator over the DEVICE-RESIDENT forest (jea_resident) + the supervisor decision WAL\n")
    S=dict(op=[-1,-1,1],vN=[1,1,0],vD=[2,3,1],lch=[-1,-1,0],rch=[-1,-1,1],N=3,root=2)   # 1/2*1/3 = 1/6
    T1=R._embed(S,0,(1,1)); T2=R._embed(S,1,(2,1))                                      # both CONTAIN S
    v1,e1,s1=evaluate(T1); m1=memo_size(); v2,e2,s2=evaluate(T2); m2=memo_size()
    print(f"  eval(T1=S+1/1)={v1} (==7/6:{v1==Fraction(7,6)})  new={e1} shared={s1}  resident forest {m1} nodes")
    print(f"  eval(T2=S*2/1)={v2} (==1/3:{v2==Fraction(1,3)})  new={e2} shared={s2}  resident forest {m2} nodes  <- S SHARED")

    # decision WAL: a stream [live, hot, live] -> recurring 'live' interns (the supervisor reuses the cached decision)
    for ev,opd in [((46,0.5),(170,0,20)), ((120,0.5),(340,1,20)), ((46,0.5),(170,0,20))]: record_decision(ev,opd)

    w_eval = (v1==Fraction(7,6)) and (v2==Fraction(1,3)) and (m2-m1 < T2["N"]) and (s2>=1)   # exact + sharing on device
    w_wal  = (wal_len()==3) and (distinct_decisions()==2)                                    # recurring decision interned
    print(f"\nW1 EXACT + DEVICE-RESIDENT SHARING (T1=7/6,T2=1/3; forest grew {m2-m1}<{T2['N']} -- S shared, computed once): {w_eval}")
    print(f"W2 DECISION WAL interned in the SAME module ({wal_len()} steps -> {distinct_decisions()} distinct; recurring evidence reused): {w_wal}")
    ok=w_eval and w_wal
    print(f"\n  {'PASS' if ok else 'FAIL'} — jea_eval is the public memoizing evaluator over the device-resident forest")
    print(f"  (jea_resident) + the decision WAL: eval-SPPF, gcd/EEA value, and decision trace, one structure; sharing")
    print(f"  is a device searchsorted, the forest grows by new nodes only. Consumed by jea_agda_apex.")
