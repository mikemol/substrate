#!/usr/bin/env python3
"""jea_sympy_bridge.py — Σ-BRIDGE: the bidirectional forest↔sympy structure↔structure bridge.

Both the interned forest (our IR) and sympy's expression tree are CANONICAL structural forms of the
same math (neither is text), so this is the SAME-CLASS case (pass 9): a structure↔structure map both
ways, round-trippable, with a FIXPOINT (forest→sympy→forest == same canonical node) as the retraction.

WHY bidirectional, why a hub (the recursive law, "why wouldn't we?"): sympy is a HUB, not a spoke.
  * sympy→forest interns sympy-expressed math into the instrument → typehole/CrossMix/consolidate/gate
    all operate on it (the on-ramp making formal objects first-class).
  * forest→sympy → then sympy's OWN canonical printers (octave_code, latex, mathml, ccode, pycode) are
    the pipeline's fan-out: build ONE bridge, inherit N generation targets. Σ-OCTAVE = forest→sympy→
    sympy.codegen('octave'), thin, downstream of here.

ASSUMPTIONS ARE NOT RESIDUE — THEY ARE CARRIER-SELECTIONS (pass-13 unification, PROVEN). A sympy
assumption (`positive=True`) is reified as a carrier child: positive-real → the lspace carrier (lspace
is the positive cone, so positivity is constitutive, not an annotation). Assumptions sympy leaves
IMPLICIT (never set) are the ONLY genuine residue — and that residue is honest: the info wasn't there.

Σ5 (IR-UNIFY-full): the bridge no longer carries its OWN flat lowerer/projector. It lowers/projects
through the UNIFIED structured vocabulary in jea_ir_unify — so sympy-origin terms intern with the SAME
structured kinds as OMML (App / Op / Subscript / Name / Constant), and ONE projector (project_unified)
serves sympy AND OMML. The flat kind="Sympy"[op] dialect, its SympyLowerer/SympyProjector, and the
hand-maintained _SYMPY_CTOR table are RETIRED (the typeholer/CrossMix can now tell Mul from sin on
sympy-origin terms). The carrier tables moved to jea_ir_unify (the self-contained vocabulary hub; this
also breaks the old bridge←unify import cycle). lower_sympy/project_sympy are kept as thin aliases so
downstream callers (jea_octave_gen) are unchanged.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, full_skeleton
import sympy as sp
# the unified vocabulary owns the lowerer/projector AND the carrier tables now (Σ5; one-way import).
from jea_ir_unify import (lower_sympy_structured, project_unified,
                          _ASSUMPTION_CARRIER, _CARRIER_ASSUMPTION, _carriers_for)   # noqa: F401 (re-export)


# the bidirectional map, both directions through the ONE structured vocabulary (no flat Sympy[op]).
lower_sympy = lower_sympy_structured       # sympy expr -> structured forest IR (the fold)
project_sympy = project_unified            # structured forest IR -> sympy expr  (the unfold; reads OMML too)


def fixpoint_test(e) -> dict:
    """forest→sympy→forest == same canonical node (the retraction, up to implicit-assumption residue)."""
    I1 = Intern(); r1 = lower_sympy(e, I1)
    back = project_sympy(I1, r1)
    I2 = Intern(); r2 = lower_sympy(back, I2)
    sk1, sk2 = full_skeleton(I1, r1), full_skeleton(I2, r2)
    return {"in": e, "back": back, "fixpoint": sk1 == sk2, "n": len(sk1),
            "back_eq": bool(sp.simplify(e - back) == 0)}


if __name__ == "__main__":
    print("=== Σ-BRIDGE: forest↔sympy via the unified structured vocabulary (Σ5) ===\n")
    x = sp.Symbol("x", positive=True); y = sp.Symbol("y"); a, b = sp.symbols("a b")

    cases = [(a * b) / (a + b), sp.sin(x) ** 2 + sp.Rational(1, 3), x * y + y]
    for e in cases:
        r = fixpoint_test(e)
        print(f"[{'FIXPOINT OK' if r['fixpoint'] else 'DRIFT'}]  ({r['n']} nodes)  {e}  ->  {r['back']}"
              f"  (back_eq={r['back_eq']})")

    # the assumption round-trips as a CARRIER: positive x -> lspace child -> back to positive=True
    print("\n--- assumption as carrier-selection (positive-real -> lspace -> positive=True) ---")
    I = Intern(); rid = lower_sympy(x, I)
    carriers = [I.nodes[c].op for c in I.nodes[rid].children if I.nodes[c].kind == "Carrier"]
    back_x = project_sympy(I, rid)
    print(f"  x(positive=True) -> Name with carriers {carriers} -> back: {back_x!r} "
          f"positive={back_x.assumptions0.get('positive')}")
    print("  (the assumption is STRUCTURE — an lspace carrier child — not a dropped tag; round-trips.)")
