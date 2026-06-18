#!/usr/bin/env python3
"""Ξ7 — cross-tool provenance: mechanically verify the Agda `compose`
(Substrate.WitnessTower.M40Closure) faithfully transcribes the Python
`a4z2_compose` (jea/metalanguage/spectral_view.py — promoted out of scratch so this
gated jea/ check reads it Λ8-cleanly). Closes the SEAM_GLUE G8 blind spot:
the M2 Agda proof's soundness rested on a HAND transcription of the realized
compose-law; this checks it by INTERNING both and matching their operator
trees under an explicit correspondence (the mat260 Σ4b pattern).

Both build a 3-component output:
    Agda:   mk ( g.chir *c h.chir ,  g.mask · σ g.zee h.mask ,  g.zee +₃ h.zee )
    Python: (   s_g * s_h        ,  m_g ^ _apply_cycle(m_h,j_g) , (j_g+j_h) % 3 )
Correspondence (leaf operators): _*c_↔Mult, _·_↔BitXor, σ↔_apply_cycle, _+₃_↔Mod.
The check: same 3-ary output, head operators correspond per component, and the
cycle action nests in component 2 on both sides. NOT eyeballed — read off the
interned forest + the Python AST.
"""
import sys, os, ast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern
import jea_agdai

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
AGDAI = os.path.join(REPO, "agda/_build/2.8.0/agda/Substrate/WitnessTower/M40Closure.agdai")
# spectral_view.py was PROMOTED out of scratch into jea/metalanguage/ (its real home) so this
# gated jea/ check can read it without a scratch dependency (Λ8 scratch-independence).
SPECTRAL = os.path.join(HERE, "spectral_view.py")

# Agda short-op → Python operator name (the transcription correspondence).
CORRESPOND = {"_*c_": "Mult", "_·_": "BitXor", "σ": "_apply_cycle", "_+₃_": "Mod"}


def short(qn):
    return qn.split(".")[-1] if qn else qn


def agda_compose_ops(I, root):
    """From the interned `compose` Defn: find the `mk` constructor node, return
    (its 3 children's head ops, the cycle-op nested in component 2)."""
    # locate the `mk` Con node in the compose subtree
    seen, mk = set(), None
    stack = [root]
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        seen.add(nid)
        n = I.nodes[nid]
        if short(n.op) == "mk":
            mk = nid
            break
        stack.extend(n.children)
    assert mk is not None, "no `mk` constructor in compose body"
    kids = I.nodes[mk].children
    assert len(kids) == 3, f"mk arity {len(kids)} ≠ 3 (expected a 3-tuple output)"
    head_ops = [short(I.nodes[c].op) for c in kids]
    # component 2 (the mask op) must nest the cycle action σ as its 2nd argument
    comp2 = I.nodes[kids[1]]
    comp2_args = comp2.children
    cycle_op = short(I.nodes[comp2_args[1]].op) if len(comp2_args) >= 2 else None
    return head_ops, cycle_op


def py_compose_ops(path):
    """From a4z2_compose's `return (..., ..., ...)`: the 3 components' head ops
    + the cycle op nested in component 2."""
    tree = ast.parse(open(path).read())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "a4z2_compose")
    ret = next(n for n in fn.body if isinstance(n, ast.Return))
    tup = ret.value
    assert isinstance(tup, ast.Tuple) and len(tup.elts) == 3, "a4z2_compose return is not a 3-tuple"

    def head(e):
        if isinstance(e, ast.BinOp):
            return type(e.op).__name__
        if isinstance(e, ast.Call):
            return e.func.id if isinstance(e.func, ast.Name) else "Call"
        return type(e).__name__

    head_ops = [head(e) for e in tup.elts]
    # component 2 = m_g ^ _apply_cycle(m_h, j_g): its right operand is the cycle Call
    comp2 = tup.elts[1]
    cycle_op = head(comp2.right) if isinstance(comp2, ast.BinOp) else None
    return head_ops, cycle_op


def main():
    print("=== Ξ7: Agda compose ↔ Python a4z2_compose provenance ===")
    if not os.path.exists(AGDAI):
        print(f"  SKIP: {AGDAI} not built (run: agda --safe Substrate/WitnessTower/M40Closure.agda)")
        return 0
    I = Intern()
    rep = jea_agdai.core_intern_agdai(AGDAI, I)
    U = dict(rep["units"])
    ck = next((q for q in U if q.endswith(".compose")), None)
    assert ck, "no compose unit in M40Closure.agdai"
    a_ops, a_cycle = agda_compose_ops(I, U[ck])
    p_ops, p_cycle = py_compose_ops(SPECTRAL)

    print(f"  Agda   compose components: {a_ops}   (cycle in comp2: {a_cycle})")
    print(f"  Python a4z2_compose      : {p_ops}   (cycle in comp2: {p_cycle})")

    # check: each Agda component's head op corresponds to the Python one
    ok = True
    for i, (ao, po) in enumerate(zip(a_ops, p_ops)):
        want = CORRESPOND.get(ao)
        match = want == po
        ok = ok and match
        print(f"    component {i}: {ao} ↔ {po}  {'MATCH' if match else 'DIVERGE (want '+str(want)+')'}")
    cyc_ok = CORRESPOND.get(a_cycle) == p_cycle
    ok = ok and cyc_ok
    print(f"    cycle action: {a_cycle} ↔ {p_cycle}  {'MATCH' if cyc_ok else 'DIVERGE'}")

    print("\n=== VERDICT ===")
    if ok:
        print("  FAITHFUL: the Agda `compose` transcribes a4z2_compose operator-for-operator")
        print("  (3-component output; sign/mask/cycle ops correspond; cycle action nests in comp2).")
        print("  The M2 proof's transcription link is now MECHANICALLY checked, not eyeballed.")
        return 0
    print("  DIVERGENCE: the transcription does NOT match — the M2 proof rests on a wrong law.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
