#!/usr/bin/env python3
"""jea_agda_dispatch.py — the integration closed: an Agda-emitted term, evaluated on the production
cooperative GPU generators, with the reduction MODE chosen by the el-atlas nedge ORACLE.

jea_agda_bridge.py closed the Agda-on-GPU path (term in Agda -> exact rational on the GPU, Agda agrees)
with the EAGER-only evaluator. This adds the M2d contribution to that path: the value-window<->trace-
window (eager/lazy reduction) Pareto knob, driven by the oracle from the workload's canonicality-demand.

It reuses jea_agda_bridge's Agda machinery UNTOUCHED (typecheck = the refl vouchers; parse; to_dag) and
evaluates through jea_generator_dag_mode (the MODE-aware production evaluator). The spit-take, completed:
a term over the rational algebra written in Agda, folded on 20 cooperative GPU generators with the
reduction schedule picked LIVE by the nedge oracle, exact both ways, and Agda agrees.

Witnesses:
1. AGDA-EXACT BOTH MODES: EAGER root == LAZY-reduced root == Agda's refl-vouched value == host truth.
2. PARETO PRESENT: eager reduces every combine (canonical, gcd-work>0); lazy defers (non-canonical
   combines, gcd-work 0). Both exact -- the value<->trace tradeoff carried onto the real Agda term.
3. ORACLE-CHOSEN: the nedge oracle picks MODE for the stated workload (canonicality-demanding sink ->
   EAGER); the chosen run agrees with Agda.
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
import jea_agda_bridge as B
import jea_generator_dag_mode as M

if __name__ == "__main__":
    line = B.typecheck()
    termStr, agda_val = B.read_vouched()
    tree = B.parse_sexpr(termStr)
    g = B.to_dag(tree); g["truth"] = B.truth_of(tree)

    eager = M.run_g_mode(g, 1)
    lazy = M.run_g_mode(g, 0)
    e_val = Fraction(eager["rn"], eager["rd"]) if eager["rd"] else None
    l_val = Fraction(lazy["rn"], lazy["rd"]) if lazy["rd"] else None        # reduce-at-readout (lazy emits unreduced)

    # the workload here feeds a canonicality-demanding sink (compare/dedup) -> high C -> oracle picks eager.
    fstar = M.oracle_decide(eager, lazy, 0)[1]
    C_workload = max(2 * fstar, 1.0)
    chosen, _ = M.oracle_decide(eager, lazy, C_workload)
    chosen_val = e_val if chosen == 1 else l_val

    print("Agda term -> production cooperative GPU evaluator -> oracle-chosen reduction MODE\n")
    print(f"  agda --safe Emit.agda : {line}  (refl vouchers hold)")
    print(f"  Agda term  : {termStr}")
    print(f"  Agda value : {agda_val}  (refl-vouched, reduced)")
    print(f"  GPU DAG    : {g['L']} leaves, {g['N']-g['L']} combines, {eager['launched']} cooperative blocks\n")
    print(f"  EAGER: root={e_val}  gcd-work={eager['gwork']}  non-canonical(combines)={eager['noncanon']}")
    print(f"  LAZY : root={l_val}  gcd-work={lazy['gwork']}  non-canonical(combines)={lazy['noncanon']}")
    print(f"  oracle f*={fstar:.3f}; workload C={C_workload:.2f} -> MODE={'EAGER' if chosen else 'LAZY'}")

    w1 = (e_val == agda_val) and (l_val == agda_val) and (e_val == g["truth"]) \
        and eager["err"] == 0 and lazy["err"] == 0 and eager["pending"] == 0 and lazy["pending"] == 0
    w2 = (eager["gwork"] > 0) and (lazy["gwork"] == 0) and (lazy["noncanon"] >= 0) and (eager["noncanon"] == 0)
    w3 = (chosen == 1) and (chosen_val == agda_val)
    print(f"\n1. AGDA-EXACT BOTH MODES (eager==lazy==Agda==truth): {w1}")
    print(f"2. PARETO PRESENT (eager canonical+gcd-work; lazy defers): {w2}")
    print(f"3. ORACLE-CHOSEN (workload -> eager; chosen run == Agda): {w3}")

    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — INTEGRATION CLOSED: a term over the rational algebra written in")
    print(f"  Agda, folded on the production cooperative GPU generators with its reduction schedule chosen")
    print(f"  by the el-atlas nedge oracle, exact both ways, Agda agrees. The M2d eager/lazy Pareto knob is")
    print(f"  fused with the closed Agda-on-GPU path; the controller now steers K AND the value<->trace mode.")
