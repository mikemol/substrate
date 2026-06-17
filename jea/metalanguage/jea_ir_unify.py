#!/usr/bin/env python3
"""jea_ir_unify.py — Σ-IR-UNIFY: ONE structured forest-IR vocabulary both front-ends lower into.

THE DUPLICATION (found by reading the two lowerers, as the typeholer would): there are TWO forest-IR
dialects, and jea_omml_octave.omml_ir_to_sympy (~20 lines) exists ONLY to translate between them:
  * sympy dialect (jea_sympy_bridge): FLAT -- every composite is kind="Sympy", op=funcname (Mul/Add/
    Pow/sin all one kind, structure buried in the op-string).
  * OMML dialect (jea_omml): STRUCTURED -- App / BinOp / Subscript / Args (structure in the KIND).

THE COMMON STRUCTURE (recursive law -- "which dialect is canonical?" is the wrong question): neither.
The structured vocabulary is what BOTH are shadows of. The sympy dialect is UNDER-structured exactly
where it hides information from the instrument (the typeholer/CrossMix key on the KIND; flat Sympy[op]
makes Mul and sin look alike to a kind-based readout; App vs Op would not). So unification = PROMOTE
the sympy lowerer to emit the structured kinds, and the translator DISSOLVES (OMML-IR and sympy-IR
become the SAME vocabulary; project_sympy reads both). Strictly more explicit, no loss (the flat op
name is kept -- as the App function name or the Op operator).

THE n-ary / binary RECONCILIATION (the real conservation-of-difficulty point): sympy Add/Mul are
N-ARY (a+b+c = one Add, 3 args); OMML BinOp is BINARY. Recursive law: a binary op is the arity-2 case
of an n-ary op; an n-ary op is a fold of the binary one. So the unified kind `Op` is N-ARY-TOLERANT
(k>=2 children); OMML's binary BinOp is the k=2 special case, read IDENTICALLY. (Same dissolution as
Σ-BRIDGE's unary-vs-binary predicate: different child-count, same kind.)

THE UNIFIED VOCABULARY (structured, n-ary-tolerant):
  Name(op=ident)                 identifiers (both dialects already agree)
  Constant(op=value, lit=...)    literals (value in the KEY -- the int-key fix)
  App(Name(fn), *args)           explicit application (OMML m:func; sympy Function & elementary fns)
  Op(op=OPNAME, *operands)       n-ary operator: sympy Add/Mul (n-ary) AND OMML BinOp (k=2) both -> here
  Subscript(base, index)         subscripts (both dialects agree)
  Carrier(op=name)               assumption-carriers (positive->lspace; sympy side)

This module: the func-name classifier + a structured sympy lowerer emitting it, + the proof that
(a) it round-trips and (b) OMML's binary BinOp is the k=2 Op (so one project handles both). PROPOSAL
for the integrating session -- does NOT edit the canonical jea_omml.py; shows the seam where the
dialects merge so omml_ir_to_sympy can retire."""
from __future__ import annotations
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR, full_skeleton
import sympy as sp

_IDENT = re.compile(r"^[A-Za-z_]\w*$")


def _name_to_sympy(txt: str, asm: dict):
    """A Name's text -> sympy. Absorbs jea_omml_octave._name_to_sympy so project_unified is a TRUE
    superset of omml_ir_to_sympy (which then retires): OMML edge runs ("()" no-op, "i−1" expression)
    AND plain identifiers (carrying any carrier-asserted assumptions, the sympy side)."""
    if txt == "()":
        return sp.Symbol("unit")                          # the ECB no-op state update
    nt = txt.replace("−", "-")                            # U+2212 -> ASCII
    if _IDENT.match(nt):
        return sp.Symbol(nt, **asm)
    try:
        return sp.sympify(nt)                             # an expression-run ("i-1") -> sympy's parser
    except Exception:
        return sp.Symbol(re.sub(r"\W", "_", txt), **asm)

# sympy func-name -> unified Op operator name (the n-ary operators). Pow stays binary (it IS binary).
_SYMPY_OP = {"Add": "Add", "Mul": "Mult", "Pow": "Pow"}
# elementary functions -> App (explicit application), same as OMML m:func.
_SYMPY_FUNC = {"sin", "cos", "tan", "exp", "log", "sqrt", "Abs"}


class StructuredSympyLowerer:
    """sympy expr -> the UNIFIED structured IR (App/Op/Subscript/Name/Constant), NOT flat Sympy[op]."""
    def __init__(self, intern: Intern):
        self.I = intern

    def _carrier_children(self, sym):
        from jea_sympy_bridge import _ASSUMPTION_CARRIER, _carriers_for
        return tuple(self.I.intern(IR(kind="Carrier", op=_ASSUMPTION_CARRIER[f], children=()))
                     for f in _carriers_for(sym))

    def lower(self, e) -> int:
        if isinstance(e, sp.Symbol):
            return self.I.intern(IR(kind="Name", op=e.name,
                                    children=self._carrier_children(e), payload=(e.name,)))
        if isinstance(e, sp.Integer):
            return self.I.intern(IR(kind="Constant", lit="int", op=str(int(e)),
                                    children=(), payload=(str(int(e)),)))
        if isinstance(e, sp.Rational):
            return self.I.intern(IR(kind="Constant", lit="rational", op=f"{e.p}/{e.q}",
                                    children=(), payload=(str(e.p), str(e.q))))
        if isinstance(e, sp.Float):
            return self.I.intern(IR(kind="Constant", lit="float", op=str(e), children=(), payload=(str(e),)))
        fn = type(e).__name__
        kids = tuple(self.lower(a) for a in e.args)
        if fn in _SYMPY_OP:                              # n-ary operator -> Op (binary = k=2 case)
            return self.I.intern(IR(kind="Op", op=_SYMPY_OP[fn], children=kids))
        if fn in _SYMPY_FUNC or isinstance(e, sp.Function):   # explicit application -> App
            fname = self.I.intern(IR(kind="Name", op=fn, children=(), payload=(fn,)))
            return self.I.intern(IR(kind="App", children=(fname,) + kids))
        # unknown composite: keep as App over its class name (total, no silent drop)
        fname = self.I.intern(IR(kind="Name", op=fn, children=(), payload=(fn,)))
        return self.I.intern(IR(kind="App", children=(fname,) + kids))


def lower_sympy_structured(e, intern: Intern) -> int:
    return StructuredSympyLowerer(intern).lower(e)


# the UNIFIED projector: reads the structured vocabulary back to sympy. Handles n-ary Op by folding;
# OMML's binary BinOp(op=...) is accepted as the k=2 Op (read identically) -- the dialects merged.
_OP_SYMPY = {"Add": sp.Add, "Mult": sp.Mul, "Mult ": sp.Mul, "Pow": sp.Pow, "Sub": lambda a, b: a - b,
             "Div": lambda a, b: a / b, "Xor": sp.Function("bitxor")}


def project_unified(I: Intern, nid: int):
    n = I.nodes[nid]
    k = n.kind
    if k == "Name":
        from jea_sympy_bridge import _CARRIER_ASSUMPTION
        asm = {_CARRIER_ASSUMPTION[I.nodes[c].op]: True for c in n.children
               if I.nodes[c].kind == "Carrier" and I.nodes[c].op in _CARRIER_ASSUMPTION}
        return _name_to_sympy(n.op or (n.payload[0] if n.payload else "_"), asm)
    if k == "Constant":
        if n.lit == "int":      return sp.Integer(int(n.op))
        if n.lit == "rational": p, q = n.op.split("/"); return sp.Rational(int(p), int(q))
        if n.lit == "float":    return sp.Float(n.op)
    if k == "App":
        fn = I.nodes[n.children[0]]; fname = fn.op or (fn.payload[0] if fn.payload else "f")
        return sp.Function(fname)(*[project_unified(I, c) for c in n.children[1:]])
    if k in ("Op", "BinOp"):                              # BinOp = the k=2 Op (dialects merged here)
        ctor = _OP_SYMPY.get(n.op)
        if ctor is None:
            raise KeyError(f"no Op mapping for {n.op!r}")
        args = [project_unified(I, c) for c in n.children]
        if n.op in ("Add", "Mult", "Pow"):
            return ctor(*args)                            # n-ary fold (sympy handles)
        out = args[0]
        for a in args[1:]:
            out = ctor(out, a)                            # binary fold for Sub/Div/Xor
        return out
    if k == "Subscript":
        base = I.nodes[n.children[0]]; bn = base.op or (base.payload[0] if base.payload else "s")
        return sp.Function(bn)(project_unified(I, n.children[1]))
    if k == "Args":                                       # OMML argument-list (non-func multi-delimiter)
        return sp.Tuple(*[project_unified(I, c) for c in n.children])
    raise KeyError(f"project_unified: unhandled kind {k!r}")


if __name__ == "__main__":
    print("=== Σ-IR-UNIFY: one structured vocabulary; the sympy/OMML dialects merge ===\n")
    a, b, c, x = sp.symbols("a b c x")

    # 1) structured sympy lowering round-trips (the promotion preserves everything flat Sympy carried)
    print("--- structured sympy lowering: fixpoint ---")
    for e in [(a*b)/(a+b), sp.sin(x)**2 + sp.Rational(1, 3), a + b + c, (a-b)**2]:
        I1 = Intern(); r1 = lower_sympy_structured(e, I1)
        back = project_unified(I1, r1)
        I2 = Intern(); r2 = lower_sympy_structured(back, I2)
        ok = full_skeleton(I1, r1) == full_skeleton(I2, r2)
        print(f"  [{'OK' if ok else 'DRIFT'}]  {e}  ->  {back}")

    # 2) the n-ary/binary reconciliation: a+b+c is ONE Op with 3 children (sympy n-ary)
    I = Intern(); r = lower_sympy_structured(a + b + c, I)
    n = I.nodes[r]
    print(f"\n--- n-ary: a+b+c -> kind={n.kind!r} op={n.op!r} with {len(n.children)} children (n-ary Op) ---")

    # 3) OMML's BINARY BinOp is the k=2 Op -- project_unified reads it IDENTICALLY (dialects merged)
    I3 = Intern()
    av = I3.intern(IR(kind="Name", op="a", payload=("a",), children=()))
    bv = I3.intern(IR(kind="Name", op="b", payload=("b",), children=()))
    omml_binop = I3.intern(IR(kind="BinOp", op="Add", children=(av, bv)))   # OMML-dialect binary node
    print(f"--- OMML binary BinOp(Add,a,b) read by the UNIFIED projector -> {project_unified(I3, omml_binop)} ---")
    print("  (BinOp accepted as the k=2 Op; project_unified reads BOTH dialects -> omml_ir_to_sympy retires)")
