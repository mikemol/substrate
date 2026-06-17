#!/usr/bin/env python3
"""jea_omml_octave.py — Σ-next / IR-BRIDGE: OMML-IR → sympy → {Octave, LaTeX, …}, end-to-end.

The seam that closes the user's mat260 loop: authored OMML cipher math → an executable Octave .m (and,
for free, LaTeX / MathML / C). Σ-OMML (jea_omml) lowers OMML to forest IR in kinds App/BinOp/Subscript/
Name; Σ-BRIDGE's project_sympy handles a DIFFERENT vocabulary (the sympy-lowered Name/Constant/Sympy).
This module is the missing translation between them: `omml_ir_to_sympy` maps the OMML-IR kinds to sympy.

ONCE the forest node is a sympy expr, sympy's OWN canonical printers are the fan-out (the Σ-BRIDGE
hub thesis): octave_code / latex / mathml / ccode all apply to the same expr -- build ONE IR-bridge,
inherit N targets. So this module's load-bearing piece is `omml_ir_to_sympy` (~20 lines); the emitters
are sympy's, stood upon (octave via codegen, exactly as Σ-OCTAVE; latex via sp.latex).

The cipher-vocabulary mapping (validated on the mat260 corpus):
  App(Name(F), *args)   -> sympy Function F applied        E(k,p)        -> E(k, p)
  BinOp[Xor](a,b)       -> Function bitxor (Octave native) p ⊕ s_{i-1}   -> bitxor(p, s(i-1))
  BinOp[Add/Sub/Mult/Div] -> the sympy infix op
  Subscript(base, sub)  -> IndexedBase(base)[sub]          s_{i-1}       -> s(i - 1)
  Name(identifier)      -> Symbol;  Name("i−1") (operator text) -> sympy's OWN parser -> i - 1
  Name("()")            -> Symbol("unit")  (the ECB no-op state)
"""
from __future__ import annotations
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern
from jea_omml import lower_omml
from jea_octave_gen import _passthrough          # reuse Σ-OCTAVE's translator-seam default
import sympy as sp
from sympy.utilities.codegen import codegen

_IDENT = re.compile(r"^[A-Za-z_]\w*$")
_BINOP = {
    "Add":  lambda a, b: a + b,
    "Sub":  lambda a, b: a - b,
    "Mult": lambda a, b: a * b,
    "Div":  lambda a, b: a / b,
    "Xor":  lambda a, b: sp.Function("bitxor")(a, b),     # ⊕ -> Octave's native bitxor
}


def _name_to_sympy(t: str):
    if t == "()":
        return sp.Symbol("unit")                          # the ECB no-op state update
    nt = t.replace("−", "-")                              # U+2212 minus -> ASCII
    if _IDENT.match(nt):
        return sp.Symbol(nt)
    try:
        return sp.sympify(nt)                             # an expression-run ("i-1") -> sympy's own parser
    except Exception:
        return sp.Symbol(re.sub(r"\W", "_", t))           # last resort: a sanitized identifier


def omml_ir_to_sympy(I: Intern, nid: int):
    """THE IR-bridge: an OMML-lowered forest node -> a sympy expression. Recursive over the OMML-IR kinds."""
    n = I.nodes[nid]
    k = n.kind
    if k == "Name":
        return _name_to_sympy(n.op or (n.payload[0] if n.payload else "_"))
    if k == "App":
        fn = I.nodes[n.children[0]]
        fname = fn.op or (fn.payload[0] if fn.payload else "f")
        return sp.Function(fname)(*[omml_ir_to_sympy(I, c) for c in n.children[1:]])
    if k == "BinOp":
        op = _BINOP.get(n.op)
        if op is None:
            raise KeyError(f"omml_ir_to_sympy: no BinOp mapping for {n.op!r}")
        return op(omml_ir_to_sympy(I, n.children[0]), omml_ir_to_sympy(I, n.children[1]))
    if k == "Subscript":
        base = I.nodes[n.children[0]]
        base_name = base.op or (base.payload[0] if base.payload else "s")
        idx = omml_ir_to_sympy(I, n.children[1])
        # emit s(i-1): in Octave indexing and calls are syntactically identical, so a Function gives the
        # right text WITHOUT triggering sympy codegen's Indexed array-loop machinery (which rejects a
        # scalar output). (The index/call conflation is Octave's own -- resolved by its runtime, not us.)
        return sp.Function(base_name)(idx)
    if k == "Args":
        return sp.Tuple(*[omml_ir_to_sympy(I, c) for c in n.children])
    if k == "Constant":
        v = n.op or (n.payload[0] if n.payload else "0")
        return sp.sympify(v.replace("−", "-"))
    raise KeyError(f"omml_ir_to_sympy: unhandled OMML-IR kind {k!r}")


def omml_to_sympy(omml_str: str, intern: Intern | None = None):
    """Lower one OMML string and bridge it to sympy. Returns (expr, partitions, intern)."""
    I = intern or Intern()
    root, parts = lower_omml(omml_str, I)
    return omml_ir_to_sympy(I, root), parts, I


def omml_to_octave(omml_str: str, name: str, arg_order=None, translator=_passthrough) -> dict:
    """END-TO-END: OMML -> forest -> sympy -> Octave .m (standing on sympy.codegen, as Σ-OCTAVE).
    Also returns the LaTeX rendering -- the SAME expr, a second printer, for free (the hub payoff)."""
    expr, parts, _ = omml_to_sympy(omml_str)
    kw = {"header": False, "empty": True}
    if arg_order is not None:
        kw["argument_sequence"] = tuple(arg_order)
    octave = codegen((name, expr), "octave", **kw)[0][1]
    return {"octave": octave, "matlab": translator(octave), "latex": sp.latex(expr),
            "expr": expr, "partitions": parts}


# the same 3 real mat260 manifest entries Σ-OMML embeds (self-contained; no cross-repo path dep).
_SAMPLES = {
    "ECB_output": ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr>'
                   '<m:e><m:r>k</m:r></m:e><m:e><m:r>p</m:r></m:e></m:d></m:e></m:func></m:oMath>'),
    "CBC_stUpd":  ('<m:oMath><m:func><m:fName><m:r>E</m:r></m:fName><m:e><m:d><m:dPr>'
                   '<m:begChr m:val="("/><m:endChr m:val=")"/><m:sepChr m:val=","/></m:dPr>'
                   '<m:e><m:r>k</m:r></m:e><m:e><m:brk/><m:d><m:dPr><m:begChr m:val="("/>'
                   '<m:endChr m:val=")"/></m:dPr><m:e><m:r>p</m:r><m:r>⊕</m:r><m:sSub><m:e>'
                   '<m:r>s</m:r></m:e><m:sub><m:r>i−1</m:r></m:sub></m:sSub></m:e></m:d></m:e>'
                   '</m:d></m:e></m:func></m:oMath>'),
}


if __name__ == "__main__":
    print("=== Σ-next / IR-BRIDGE: OMML → sympy → {Octave, LaTeX} end-to-end ===\n")
    for name, omml in _SAMPLES.items():
        out = omml_to_octave(omml, name)
        print(f"--- {name} ---")
        print(f"  sympy : {out['expr']}")
        print(f"  latex : {out['latex']}")
        print("  octave:")
        for ln in out["octave"].splitlines():
            print("    " + ln)
        print()
    print("One IR-bridge (omml_ir_to_sympy) -> sympy -> N printers (octave, latex shown; mathml/ccode")
    print("inherited). The mat260 loop closes: authored OMML cipher math -> executable Octave .m.")
