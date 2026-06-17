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
assumption (`positive=True`) is reified as a REGISTERED OBLIGATION (the type-hole = CrossMul =
predicate node-kind, one object). To the extent it has a STANDING CARRIER it is discharged by
carrier-selection: positive-real → the lspace carrier (the lspace→exp detour IS its discharge; lspace
is the positive cone, so positivity is constitutive, not an annotation). The obligation discharges
through the SAME resolve(·, domain) path as a binary OMML partition (a predicate = a partition between
the REFINED and UNREFINED reading; VERIFIED unary≡binary, no new mechanism). Assumptions sympy leaves
IMPLICIT (never set) are the ONLY genuine residue — and that residue is honest: the info wasn't there.

  assumption (explicit)  ->  carrier-selection (has a standing carrier: positive-real→lspace)
                         ->  OR a bare predicate-obligation (no standing carrier yet; a RECURRING one
                             is a carrier waiting to be named = a recurring type-hole is a generator).

This module: sympy→forest (walk .func/.args, register assumptions), forest→sympy (read carriers back),
fixpoint. Carrier table seeded with positive-real→lspace; extend as carriers are named."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR, full_skeleton
import sympy as sp

# ── the assumption→carrier seed table (DATA, not mechanism — the only new content, pass-13) ──
# sympy assumption flag -> a carrier op-name the symbol is interned INTO (discharge by carrier-selection).
_ASSUMPTION_CARRIER = {
    "positive": "lspace",          # positive-real -> lspace (the lspace→exp detour discharges it)
    # extend: "integer": "zmod"?, "nonnegative": ...  -- named as carriers are built
}
# the reverse: carrier op-name -> the sympy assumption it asserts on a reconstructed Symbol.
_CARRIER_ASSUMPTION = {v: k for k, v in _ASSUMPTION_CARRIER.items()}


def _carriers_for(sym: sp.Symbol) -> tuple[int, ...]:
    """The carrier nodes a symbol's EXPLICIT assumptions select. Implicit assumptions -> nothing
    (honest residue)."""
    return tuple(sorted(flag for flag in _ASSUMPTION_CARRIER
                        if sym.assumptions0.get(flag) is True))


class SympyLowerer:
    """sympy expression -> interned forest IR (the fold)."""
    def __init__(self, intern: Intern):
        self.I = intern

    def _carrier_children(self, sym: sp.Symbol) -> tuple[int, ...]:
        kids = []
        for flag in _carriers_for(sym):
            kids.append(self.I.intern(IR(kind="Carrier", op=_ASSUMPTION_CARRIER[flag], children=())))
        return tuple(kids)

    def lower(self, e) -> int:
        # atoms
        if isinstance(e, sp.Symbol):
            # a symbol interned INTO its assumption-carriers: positivity is structure (a child), not a tag
            return self.I.intern(IR(kind="Name", op=e.name,
                                    children=self._carrier_children(e), payload=(e.name,)))
        if isinstance(e, sp.Integer):
            # the VALUE is the constant's identity (atomic referent, like a free name) -> KEY (op),
            # NOT payload (payload isn't keyed -> all ints would collapse to one node: the agdai-v1 /
            # abs-vs-str bug class. distinguishing structure goes in the key.)
            return self.I.intern(IR(kind="Constant", lit="int", op=str(int(e)), children=(),
                                    payload=(str(int(e)),)))
        if isinstance(e, sp.Rational):
            return self.I.intern(IR(kind="Constant", lit="rational", op=f"{e.p}/{e.q}", children=(),
                                    payload=(str(e.p), str(e.q))))
        if isinstance(e, sp.Float):
            return self.I.intern(IR(kind="Constant", lit="float", op=str(e), children=(),
                                    payload=(str(e),)))
        # composite: func + args. the func NAME is the op (free/referential identity, like Def/builtin).
        kids = tuple(self.lower(a) for a in e.args)
        return self.I.intern(IR(kind="Sympy", op=type(e).__name__, children=kids))


# func-name -> sympy constructor, for the reverse direction (the ONE correspondence, both ways)
_SYMPY_CTOR = {
    "Mul": sp.Mul, "Add": sp.Add, "Pow": sp.Pow,
    "sin": sp.sin, "cos": sp.cos, "exp": sp.exp, "log": sp.log,
    "NegativeOne": lambda: sp.Integer(-1), "One": lambda: sp.Integer(1), "Zero": lambda: sp.Integer(0),
    "Half": lambda: sp.Rational(1, 2),
}


class SympyProjector:
    """interned forest IR -> sympy expression (the unfold). Reads carriers back as assumptions."""
    def __init__(self, intern: Intern):
        self.I = intern

    def project(self, nid: int):
        n = self.I.nodes[nid]
        if n.kind == "Name":
            # reconstruct the Symbol WITH the assumptions its carriers assert (carrier→assumption)
            asm = {}
            for c in n.children:
                cn = self.I.nodes[c]
                if cn.kind == "Carrier" and cn.op in _CARRIER_ASSUMPTION:
                    asm[_CARRIER_ASSUMPTION[cn.op]] = True
            return sp.Symbol(n.payload[0], **asm)
        if n.kind == "Constant":
            if n.lit == "int":      return sp.Integer(int(n.payload[0]))
            if n.lit == "rational": return sp.Rational(int(n.payload[0]), int(n.payload[1]))
            if n.lit == "float":    return sp.Float(n.payload[0])
        if n.kind == "Sympy":
            args = [self.project(c) for c in n.children]
            ctor = _SYMPY_CTOR.get(n.op)
            if ctor is None:
                raise KeyError(f"no sympy constructor for {n.op!r} (extend _SYMPY_CTOR)")
            if n.op in ("NegativeOne", "One", "Zero", "Half"):
                return ctor()
            return ctor(*args)
        raise KeyError(f"cannot project node kind {n.kind!r}")


def lower_sympy(e, intern: Intern) -> int:
    return SympyLowerer(intern).lower(e)

def project_sympy(intern: Intern, root: int):
    return SympyProjector(intern).project(root)


def fixpoint_test(e) -> dict:
    """forest→sympy→forest == same canonical node (the retraction, up to implicit-assumption residue)."""
    I1 = Intern(); r1 = lower_sympy(e, I1)
    back = project_sympy(I1, r1)
    I2 = Intern(); r2 = lower_sympy(back, I2)
    sk1, sk2 = full_skeleton(I1, r1), full_skeleton(I2, r2)
    return {"in": e, "back": back, "fixpoint": sk1 == sk2, "n": len(sk1),
            "back_eq": bool(sp.simplify(e - back) == 0) if e.is_number or True else None}


if __name__ == "__main__":
    print("=== Σ-BRIDGE: forest↔sympy, assumptions as carrier-selections ===\n")
    x = sp.Symbol("x", positive=True); y = sp.Symbol("y"); a, b = sp.symbols("a b")

    cases = [(a*b)/(a+b), sp.sin(x)**2 + sp.Rational(1, 3), x*y + y]
    for e in cases:
        r = fixpoint_test(e)
        print(f"[{'FIXPOINT OK' if r['fixpoint'] else 'DRIFT'}]  ({r['n']} nodes)  {e}  ->  {r['back']}")

    # the assumption round-trips as a CARRIER: positive x -> lspace child -> back to positive=True
    print("\n--- assumption as carrier-selection (positive-real -> lspace -> positive=True) ---")
    I = Intern(); rid = lower_sympy(x, I)
    carriers = [I.nodes[c].op for c in I.nodes[rid].children if I.nodes[c].kind == "Carrier"]
    back_x = project_sympy(I, rid)
    print(f"  x(positive=True) -> Name with carriers {carriers} -> back: {back_x!r} "
          f"positive={back_x.assumptions0.get('positive')}")
    print("  (the assumption is STRUCTURE — an lspace carrier child — not a dropped tag; round-trips.)")
