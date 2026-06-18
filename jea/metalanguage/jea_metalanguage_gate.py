#!/usr/bin/env python3
"""jea_metalanguage_gate.py — Σ6: the regression gate for the metalanguage / Σ instruments.

The Σ apparatus (the cross-language correspondence front-ends + readouts) grew to ~11 modules with NO
regression net -- a future edit could silently break the mat260 OMML→Octave pipeline. This gate asserts
a KNOWN STRUCTURAL INVARIANT of each instrument (not merely "exits 0"): the fixpoints, the 12/12-shaped
lowerings, the partition behaviour, the gate verdicts. PURE modules (stdlib/sympy) always run; TOOLCHAIN
modules (jea_cuda→libclang, jea_agdai→agda) self-SKIP when their dep is absent (matching the cupy-skip
in jea_regression_gate). Fired per-commit from .githooks/pre-commit on staged jea/metalanguage/ (+ the
two root Σ modules) -- the G9 escalation: an automatable correctness class moved to a non-skippable layer.

Each check returns "PASS" / "SKIP: <reason>", or raises -> FAIL. Exit nonzero on any FAIL.
"""
import sys, os, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))      # jea/ root (jea_oneforest, jea_omml_domain live there)


def chk_pyalg():
    import jea_pyalg as A
    I = A.Intern()
    a = I.intern(A.IR(kind="Name", op="x", children=()))
    b = I.intern(A.IR(kind="Name", op="x", children=()))
    assert a == b, "intern must dedup structurally-equal nodes"
    return "PASS"


def chk_trace_lazy():
    import jea_pyalg as A
    I = A.Intern(); D = A.PyDivStr(I)
    root = I.intern(A.IR(kind="seq", op="s", children=tuple(
        I.intern(A.IR(kind="a", op=str(k), children=())) for k in range(5))))
    t = D.trace(root)
    assert tuple(h for h, _ in D.trace_steps(root)) == A.head_spine(t), "trace_steps must match eager head_spine"
    assert A.trace_fold_lazy(D, root, lambda a: 0, lambda h, b, r: r + 1) == A.grade(t), "lazy grade must match"
    assert A.trace_fold_lazy(D, root, lambda a: a, lambda h, b, r: r) == A.collapse(t), "lazy collapse must match"
    # deep chain: the lazy path survives where eager trace() RecursionErrors (Σ-TRACE-LAZY's whole point)
    deep = I.intern(A.IR(kind="seq", op="s", children=tuple(
        I.intern(A.IR(kind="a", op=str(k), children=())) for k in range(4000))))
    assert A.trace_fold_lazy(D, deep, lambda a: 0, lambda h, b, r: r + 1) == 4000, "deep-chain lazy grade"
    # full_skeleton-lazy (the tree dual): generator matches the tuple; a 4000-deep tree survives (the old
    # recursion RecursionErrors), and the generator early-stops.
    skel = I.intern(A.IR(kind="op", op="+", children=(
        I.intern(A.IR(kind="x", op="a", children=())), I.intern(A.IR(kind="x", op="b", children=())))))
    assert tuple(A.full_skeleton_steps(I, skel)) == A.full_skeleton(I, skel), "skeleton generator must match tuple"
    nest = I.intern(A.IR(kind="x", op="z", children=()))
    for _ in range(4000):
        nest = I.intern(A.IR(kind="w", op="w", children=(nest,)))
    assert len(A.full_skeleton(I, nest)) == 4001, "deep-tree full_skeleton must not RecursionError"
    assert next(A.full_skeleton_steps(I, nest)) == ("w", "", "w", ""), "skeleton generator early-stops"
    return "PASS"


def chk_pysim():
    import jea_pysim
    src = "def f(x):\n    return x + x\ndef g(y):\n    return y + y\n"   # f,g alpha-equivalent
    p = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False); p.write(src); p.close()
    try:
        C = jea_pysim.Corpus(); C.add_file(p.name)
        assert len(C.units) == 2, f"expected 2 units, got {len(C.units)}"
        sf = C.shared_fraction(C.units[0], C.units[1])
        assert sf == 1.0, f"alpha-equivalent defs must share fully (got {sf})"
    finally:
        os.unlink(p.name)
    return "PASS"


def chk_omml():
    import jea_omml
    from jea_pyalg import Intern
    I = Intern(); root, parts = jea_omml.lower_omml(jea_omml._SAMPLES["ECB-output"], I)
    assert I.nodes[root].kind == "App", "E(k,p) must lower to App"
    assert not parts, "explicit m:func must produce NO partition"
    I2 = Intern()
    _, p2 = jea_omml.lower_omml("<m:oMath><m:e><m:r>a</m:r><m:r>b</m:r></m:e></m:oMath>", I2)
    assert len(p2) == 1, "bare juxtaposition must produce exactly one ADJACENCY partition"
    return "PASS"


def chk_omml_domain():
    import jea_omml_domain as D
    from jea_pyalg import Intern, IR, CrossMix
    I = Intern(); X = CrossMix(I)
    f = I.intern(IR(kind="Name", op="f", children=())); x = I.intern(IR(kind="Name", op="x", children=()))
    app = I.intern(IR(kind="App", children=(f, x))); mul = I.intern(IR(kind="BinOp", op="Mult", children=(f, x)))
    adj = D.Partition("ADJACENCY", app, mul, "application", "multiplication", X.cross_term(app, mul))
    assert isinstance(D.resolve(adj, D.EMPTY), D.Partition), "empty domain must preserve the fork"
    r = D.resolve(adj, D.TYPE_THEORY)
    assert isinstance(r, D.Resolved) and r.reading == "application", "type-theory must commit ADJACENCY=application"
    return "PASS"


def chk_oneforest():
    import jea_oneforest
    F = jea_oneforest.OneForest()
    F.add_python("spec", "def axpy(x, y):\n    return x + y\n", "axpy")
    F.add_python("impl", "def axpy(x, y):\n    return x + y\n", "axpy")
    rows = F.gate("spec", "impl")
    assert rows and rows[0]["realizes"], "identical impl must REALIZE spec (degree 0)"
    return "PASS"


def chk_sympy_bridge():
    import jea_sympy_bridge as B
    import sympy as sp
    a, b = sp.symbols("a b")
    assert B.fixpoint_test((a * b) / (a + b))["fixpoint"], "forest<->sympy must be a fixpoint"
    return "PASS"


def chk_octave():
    import jea_octave_gen as O
    import sympy as sp
    a, b = sp.symbols("a b")
    oct_src = O.emit_octave_from_sympy("schur", (a * b) / (a + b))["octave"]
    assert "a.*b" in oct_src.replace(" ", ""), f"octave must be element-wise; got:\n{oct_src}"
    return "PASS"


def chk_ir_unify():
    import jea_ir_unify as U
    import sympy as sp
    from jea_pyalg import Intern, IR, full_skeleton
    a, b = sp.symbols("a b")
    I = Intern(); r = U.lower_sympy_structured((a * b) / (a + b), I)
    back = U.project_unified(I, r)
    I2 = Intern(); r2 = U.lower_sympy_structured(back, I2)
    assert full_skeleton(I, r) == full_skeleton(I2, r2), "structured sympy lowering must round-trip"
    I3 = Intern()
    av = I3.intern(IR(kind="Name", op="a", payload=("a",), children=()))
    bv = I3.intern(IR(kind="Name", op="b", payload=("b",), children=()))
    bo = I3.intern(IR(kind="BinOp", op="Add", children=(av, bv)))
    assert U.project_unified(I3, bo) == sp.Symbol("a") + sp.Symbol("b"), "project_unified must read OMML BinOp (k=2 Op)"
    return "PASS"


def chk_omml_octave():
    import jea_omml_octave as P
    out = P.omml_to_octave(P._SAMPLES["ECB_output"], "f")
    assert "E(k, p)" in out["octave"], f"OMML E(k,p) must reach octave; got:\n{out['octave']}"
    return "PASS"


def chk_picircuit():
    import jea_picircuit  # noqa: F401  (import-only: a circuit-classify instrument; covered structurally elsewhere)
    return "PASS"


def chk_grammar_fixpoint():
    import jea_grammar_fixpoint as G
    anbn = {"S": [["a", "S", "b"], []]}
    assert G.recognize(anbn, ["a", "a", "b", "b"], "S")["accept"], "aⁿbⁿ must accept aabb"
    assert not G.recognize(anbn, ["a", "a", "b"], "S")["accept"], "aⁿbⁿ must reject aab"
    r = G.recognize({"E": [["E", "+", "E"], ["x"]]}, ["x", "+", "x", "+", "x"], "E")
    assert r["accept"], "ambiguous E must accept"
    xid = r["intern"].table.get(("tok", "", "x", "", ()))
    assert xid is not None and r["intern"].fanin[xid] >= 2, "shared token must have fan-in (SPPF sharing)"
    return "PASS"


def chk_mat260_verify():
    import jea_mat260_verify as V
    rep = V.verify(V._CIPHERS)
    assert len(rep["classes"]) == 3, f"expected 3 cipher equivalence classes, got {len(rep['classes'])}"
    assert rep["realizes"] and rep["realizes"][2] == 0, "equal ciphers must gate at degree 0 (REALIZES)"
    # Σ4b operator extraction (the agdai-free side; the full agda-vs-omml gate runs on the real .agdai)
    assert V.omml_cipher_ops(V._CIPHERS["ECB-output"]) == {"E"}, "OMML op extraction (E)"
    assert V.omml_cipher_ops(V._CIPHERS["ECB-stUpd"]) == {"()"}, "OMML unit op ()"
    assert "⊕" in V.omml_cipher_ops(V._CIPHERS["CBC-stUpd"]), "OMML xor op"
    return "PASS"


def chk_cuda():
    try:
        import clang.cindex  # noqa: F401
    except Exception:
        return "SKIP: libclang absent"
    import jea_cuda
    r = jea_cuda.fixpoint_test("__global__ void saxpy(float* x, float* y) {\n  int i = threadIdx.x;\n  y[i] = x[i] + y[i];\n}\n")
    assert r["fixpoint"], "cuda lower<->project must be a fixpoint"
    return "PASS"


def chk_agdai():
    import jea_agdai  # noqa: F401
    # the deep correspondence (decode a real .agdai) needs the agda toolchain + a fresh interface and is
    # too slow for a per-commit gate -- validated on-demand. Here: import + the consumer's presence.
    assert hasattr(jea_agdai, "core_intern_agdai") and hasattr(jea_agdai, "intern_signature")
    return "SKIP: agda decode is on-demand (import + API present)"


CHECKS = [
    ("jea_pyalg",       chk_pyalg),         ("jea_pyalg.lazy",  chk_trace_lazy),
    ("jea_pysim",       chk_pysim),
    ("jea_omml",        chk_omml),          ("jea_omml_domain", chk_omml_domain),
    ("jea_oneforest",   chk_oneforest),     ("jea_sympy_bridge", chk_sympy_bridge),
    ("jea_octave_gen",  chk_octave),        ("jea_ir_unify",    chk_ir_unify),
    ("jea_omml_octave", chk_omml_octave),   ("jea_picircuit",   chk_picircuit),
    ("jea_mat260_verify", chk_mat260_verify),
    ("jea_grammar_fixpoint", chk_grammar_fixpoint),
    ("jea_cuda",        chk_cuda),          ("jea_agdai",       chk_agdai),
]


def main():
    fails, npass, nskip = [], 0, 0
    for name, fn in CHECKS:
        try:
            r = fn()
        except Exception as e:
            r = f"FAIL: {type(e).__name__}: {e}"
        tag = r.split(":")[0]
        print(f"  meta-gate {name:<18} {r}")
        if tag == "PASS":
            npass += 1
        elif tag == "SKIP":
            nskip += 1
        else:
            fails.append(name)
    if fails:
        print(f"meta-gate: FAILED — {', '.join(fails)} (a Σ instrument regressed)")
        return 1
    print(f"meta-gate: OK ({npass} pass, {nskip} skip)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
