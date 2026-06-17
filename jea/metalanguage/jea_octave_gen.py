#!/usr/bin/env python3
"""jea_octave_gen.py — Σ-OCTAVE: forest → sympy → Octave generation (one pipeline output).

THIN by construction (pass-13 reframing): emission is NOT a hand-written emitter — it is the canonical
unparser for this edge, `sympy.codegen('octave')`, which we STAND ON (octave_code emits element-wise
ops a.*b./, matrix literals, piecewise; codegen wraps `function out = name(args) ... end`). The
substrate work was Σ-BRIDGE (forest↔sympy); Σ-OCTAVE is orchestration over it:
    forest node --(Σ-BRIDGE project_sympy)--> sympy expr --(codegen 'octave')--> .m source.

WHY one-directional (Octave is emit-only here): Octave FAILS the canonical-parser gate (context-
sensitive grammar: x(i)=index-or-call by runtime scope, a'=transpose-or-string by preceding token,
bracket-whitespace semantic). That is a READER problem; we GENERATE (structure→text from an
unambiguous source), so the ambiguity never arises. We do NOT parse Octave back. Octave's OWN RUNTIME
is the canonical check: run the .m, it works or it doesn't — no parse-back needed.

THE octave→matlab TRANSLATOR IS AN EXTERNAL SEAM, NOT OURS. It is the user's pipeline artifact (they
have a CI-capable Octave but manual MATLAB; the translator carries Octave→MATLAB for the manual submit
step). We do NOT reimplement it (that would be rebuild-don't-read on the user's own tool). Σ-OCTAVE
emits Octave and exposes a `translator` hook (a supplied callable str->str); default is passthrough so
this runs standalone, the user wires their real translator in their pipeline.

This is sympy-as-HUB realized: the SAME forest→sympy bridge feeds octave here, and latex/mathml/ccode
elsewhere, each via sympy's own canonical printer. Build one bridge, inherit N targets."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_sympy_bridge import project_sympy
from jea_pyalg import Intern
import sympy as sp
from sympy.utilities.codegen import codegen


def _passthrough(octave_src: str) -> str:
    return octave_src


def emit_octave(name: str,
                forest_root,
                intern: Intern,
                arg_order: tuple | None = None,
                outputs: list[str] | None = None,
                translator=_passthrough) -> dict:
    """Generate an Octave `.m` function from a forest node (a named formal object).

    name        : the .m function name (the formal object's name → a named function, not codegen's out1)
    forest_root : interned id of the formal object (or a list of ids for a multi-output bundle)
    intern      : the forest the id(s) live in
    arg_order   : force the signature argument order (sympy free-symbol order otherwise)
    outputs     : output variable names for a multi-output bundle (len == len(forest_root list))
    translator  : str->str hook for the user's octave→matlab translator (default passthrough)

    Returns {octave, matlab, expr, args} -- octave is the canonical-checkable source; matlab is the
    translator's output (== octave under passthrough)."""
    # forest → sympy (Σ-BRIDGE)
    if isinstance(forest_root, (list, tuple)):
        exprs = [project_sympy(intern, r) for r in forest_root]
        outs = outputs or [f"out{i+1}" for i in range(len(exprs))]
        name_expr = (name, [sp.Eq(sp.Symbol(o), e) for o, e in zip(outs, exprs)])
        all_expr = exprs
    else:
        e = project_sympy(intern, forest_root)
        name_expr = (name, e)
        all_expr = [e]

    # sympy → octave (the canonical unparser; we stand on it)
    kw = {"header": False, "empty": True}
    if arg_order is not None:
        kw["argument_sequence"] = tuple(arg_order)
    octave_src = codegen(name_expr, "octave", **kw)[0][1]

    # external seam: the user's octave→matlab translator (NOT ours)
    matlab_src = translator(octave_src)

    # collect the free symbols actually used (the signature), for the caller's record
    args = sorted({s.name for ex in all_expr for s in ex.free_symbols})
    return {"octave": octave_src, "matlab": matlab_src, "expr": all_expr, "args": args}


def emit_octave_from_sympy(name: str, expr, **kw) -> dict:
    """Convenience: skip the forest, emit directly from a sympy expr (for callers already in sympy).
    Routes through the SAME codegen path; the forest is the on-ramp, not mandatory for pure generation."""
    I = Intern()
    from jea_sympy_bridge import lower_sympy
    root = lower_sympy(expr, I)             # round-trips through the bridge (proves the forest path)
    return emit_octave(name, root, I, **kw)


if __name__ == "__main__":
    from jea_sympy_bridge import lower_sympy
    print("=== Σ-OCTAVE: forest → sympy → Octave (standing on sympy.codegen) ===\n")
    a, b, x = sp.symbols("a b x")

    # 1) a single named formal object: schur(a,b)
    I = Intern(); r = lower_sympy((a*b)/(a+b), I)
    out = emit_octave("schur", r, I, arg_order=(a, b))
    print("--- single function (forest → octave) ---")
    print(out["octave"]); 
    print(f"  args detected: {out['args']}")

    # 2) a multi-output bundle: stats(a,b) -> [m, v]
    I2 = Intern()
    rm = lower_sympy((a+b)/2, I2); rv = lower_sympy((a-b)**2, I2)
    out2 = emit_octave("stats", [rm, rv], I2, arg_order=(a, b), outputs=["m", "v"])
    print("--- multi-output bundle ---")
    print(out2["octave"])

    # 3) the translator seam (a stub octave→matlab: e.g. % comments -> %, or .^ untouched; here a marker)
    def demo_translator(s):  # stands in for the USER's real translator
        return "% (translated to MATLAB dialect by user's tool)\n" + s
    out3 = emit_octave("schur", r, I, arg_order=(a, b), translator=demo_translator)
    print("--- translator seam (user's octave→matlab tool plugs in here) ---")
    print(out3["matlab"])
    print("  (default is passthrough; Octave runtime is the canonical check on out['octave'])")
