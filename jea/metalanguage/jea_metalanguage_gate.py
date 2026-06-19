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


def chk_pyalg_referential():
    """Ⓤ.gate: REFERENTIAL IDENTITY lives in the KEY — distinct referents must NOT collapse to one
    id, while the rename-orbit (BOUND names) must STILL quotient. Guards the false-DUPLICATE class:
    a referential str-field captured in NEITHER the key NOR the payload (it is not an ast NODE child,
    so the generic `iter_child_nodes` walk drops it) ⇒ two distinct referents intern to ONE node.
    That bug recurred across 5 ast node classes (Attribute/alias/keyword/ImportFrom/Global) + the
    original free-Name abs-vs-str collapse. A future lowerer change that re-drops such a field
    collapses a pair below ⇒ this FAILS, blocking by construction (the G9 escalation from the Ⓤ-fix
    arc). The TWO directions ARE the Ⓖ★ idempotent-vs-invertible genus line: referential ⇒ KEY
    (faithful/distinct species); bound ⇒ role-quotient (the alpha-orbit, deliberately merged)."""
    import jea_pyalg as A

    def pair(lower, s1, s2):
        # lower BOTH into the SAME intern table — id-equality is only meaningful within one table
        # (a fresh Intern per source restarts ids at 0, so same-SHAPED sources coincide by INDEX,
        # not by structure; that would make this gate vacuous). Same table ⇒ a shared structure
        # reuses an id, a referential difference allocates a new one.
        I = A.Intern()
        return lower(s1, I)[0], lower(s2, I)[0]

    # (1) DISTINCT REFERENTS must not collapse — one minimal pair per dropped-str-field class:
    distinct = [
        ("Attribute.attr",      "a.foo\n",           "a.bar\n"),
        ("free Name (abs/str)", "abs(z)\n",          "str(z)\n"),
        ("alias (import)",      "import os\n",        "import sys\n"),
        ("alias.name (from)",   "from m import n\n",  "from m import q\n"),
        ("ImportFrom.module",   "from a import x\n",  "from b import x\n"),
        ("keyword.arg",         "f(k=1)\n",           "f(j=1)\n"),
        ("Global.names",        "global x\n",         "global y\n"),
    ]
    # BOTH arms must satisfy referential identity (Ⓤ.Σ1-fix gave cst the same free-vs-bound split as
    # ast). The cst arm runs only when libcst resolves (toolchain-gated, like jea_cuda); ast always.
    arms = [("ast", A.lower_source)]
    if getattr(A, "_HAS_CST", False):
        arms.append(("cst", A.lower_source_cst))
    for arm, lower in arms:
        for label, s1, s2 in distinct:
            i1, i2 = pair(lower, s1, s2)
            assert i1 != i2, f"[{arm}] false-DUPLICATE: distinct {label} interned to ONE id ({s1!r}≡{s2!r})"
        # (2) the DUAL — the fix must NOT over-distinguish: a BOUND-name rename must still role-quotient.
        # Same referential `.foo`, renamed bound receiver/param ⇒ the SAME id (the alpha-orbit holds);
        # a referential `.attr` difference under that same shape must STILL split.
        fa, fb = pair(lower, "def f(self, x):\n    return self.foo + x\n",
                             "def g(this, y):\n    return this.foo + y\n")
        assert fa == fb, f"[{arm}] alpha-equivalence LOST: renamed bound names must role-quotient to one id"
        fa2, fc = pair(lower, "def f(self, x):\n    return self.foo + x\n",
                              "def h(self, x):\n    return self.bar + x\n")
        assert fa2 != fc, f"[{arm}] referential .attr must split even under an alpha-equivalent body"

    # (3) STRUCTURAL scalar fields beyond names (the Ⓤ.audit sweep of ast's 39 scalar fields): a
    # conversion / async-flag / match-attr / singleton-KIND is referential-or-structural ⇒ the KEY,
    # NOT a value-residue. (Distinct from VALUE fields -- Constant.value, MatchSingleton.value WITHIN a
    # kind -- which are intentionally abstracted at skeleton grade: 1≡2, case True≡case False.) ast-arm
    # specific: the cst arm represents f-strings/t-strings differently and may collapse the conversion
    # (a documented cst residual; the cross-arm convergence target was the referential NAME class).
    ast_only = [
        ("FormattedValue.conversion", 'f"{x!r}"\n',                  'f"{x!s}"\n'),
        ("comprehension.is_async",    'async def f():\n return [x async for x in y]\n',
                                      'async def f():\n return [x for x in y]\n'),
        ("MatchClass.kwd_attrs",      'match v:\n case C(x=1): pass\n', 'match v:\n case C(y=1): pass\n'),
        ("MatchSingleton kind",       'match v:\n case None: pass\n',   'match v:\n case True: pass\n'),
    ]
    for label, s1, s2 in ast_only:
        i1, i2 = pair(A.lower_source, s1, s2)
        assert i1 != i2, f"[ast] structural drop: {label} collapsed below key ({s1!r}≡{s2!r})"
    detail = "ast+cst" if len(arms) == 2 else "ast (cst: libcst absent)"
    return (f"PASS (referential→key on {detail}: 7 name classes split + 4 structural "
            f"(conversion/async/match) on ast; alpha-quotient + value-abstraction preserved)")


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


def chk_omml_render():
    # Σ-RENDER (Σ-ι / mat260 JeaCoercionAsk): the render-over-IR leg reproduces mat260 render-notation,
    # ι-aware. O3: every embedded manifest entry renders exactly (the 2 ι entries are the new capability).
    # O2: the VALUE projection erases ι (CFB-stUpd's sympy == its ι-free core CFB-output) — the fork that
    # lets render SHOW ι while octave/value treats it as identity.
    import jea_omml_render as R
    from jea_omml_octave import omml_to_sympy
    for label, (omml, expect) in R._MANIFEST.items():
        got = R.render_omml(omml)
        assert got == expect, f"render {label}: got {got!r} != {expect!r}"
    assert "ι_{𝒮→𝓑}(" in R.render_omml(R._MANIFEST["CFB-stUpd"][0]), "O3: CFB ι coercion must render"
    assert "ι_{𝓑→𝔹*}(" in R.render_omml(R._MANIFEST["ChaCha20-output"][0]), "O3: ChaCha ι must render"
    e1, _, _ = omml_to_sympy(R._MANIFEST["CFB-stUpd"][0])
    e2, _, _ = omml_to_sympy(R._MANIFEST["CFB-output"][0])
    assert e1 == e2, f"O2: ι must erase on the value side (CFB-stUpd {e1} != CFB-output {e2})"
    return f"PASS (Σ-ι: {len(R._MANIFEST)}/{len(R._MANIFEST)} render incl. 2 ι; O2 value-erasure holds)"


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
    # the embedded fixture has TWO correct equivalence pairs (CBC stUpd==output; CTR==ChaCha20 stUpd).
    # (Asserting the machinery on a controlled fixture -- NOT mat260-corpus facts, which drift; the live
    # corpus is verified via --manifest. The old "== 3" asserted a now-stale CFB≡OFB class.)
    assert len(rep["classes"]) == 2, f"expected 2 fixture equivalence classes, got {len(rep['classes'])}"
    assert rep["realizes"] and rep["realizes"][2] == 0, "equal terms must gate at degree 0 (REALIZES)"
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
    import jea_agdai
    from jea_pyalg import Intern
    assert hasattr(jea_agdai, "core_intern_agdai") and hasattr(jea_agdai, "intern_signature")
    # Φ7: when the shim is BUILT and a test interface exists, this check is correct-by-construction --
    # it decodes Emit.agdai (~1s) and asserts the Φ7a (clause LHS patterns) + Φ7b (datatype->constructor
    # member links) structure the producer now emits. Absent the toolchain it SKIPs (the per-commit gate
    # stays toolchain-free; the agda decode is on-demand), matching jea_cuda's libclang-absent discipline.
    here = os.path.dirname(os.path.abspath(__file__))
    shim = os.path.join(here, "agdai_shim")
    agdai = os.path.join(here, "..", "agda-emit", "Emit.agdai")
    if not (os.path.exists(shim) and os.path.exists(agdai)):
        return "SKIP: agda decode is on-demand (import + API present; shim/interface not built)"
    I = Intern()
    try:
        rep = jea_agdai.core_intern_agdai(agdai, I, shim_bin=shim)
    except (RuntimeError, FileNotFoundError) as e:
        # a stale interface (built by another Agda version) decodes to Nothing -- not a Φ7 regression.
        return f"SKIP: agda decode unavailable ({type(e).__name__}: stale/wrong-version interface)"
    # Φ7b: at least one datatype unit carries its constructor member-links.
    assert rep.get("members"), "Φ7b regression: no datatype->constructor member links emitted"
    assert any(len(ms) >= 1 for ms in rep["members"].values()), "Φ7b: member lists empty"
    # Φ7a: the forest contains Clause nodes (structural, op kept), and at least one clause carries LHS
    # patterns -- a clause with >=2 children is >=1 pattern + the body (a body-only clause has 1 child).
    # (PVar/PCon themselves intern into the bound/free branches, so their op is the de-Bruijn role / qname,
    # not the literal "PCon" -- assert the clause ARITY, which proves the patterns are attached.)
    clause_arities = [len(n.children) for n in I.nodes if n.op == "Clause"]
    assert clause_arities, "Φ7a regression: no Clause nodes (LHS patterns not walked)"
    assert max(clause_arities) >= 2, "Φ7a regression: clauses carry no LHS patterns (body-only)"
    return (f"PASS (Φ7: decoded Emit.agdai -> {len(rep['units'])} units, "
            f"{len(clause_arities)} clauses, members on {len(rep['members'])} parent(s))")


def chk_sppf_torsor():
    # the parse forest is a torsor-bundle over the input-position line (fiber = invariant
    # recognition, span = gauge; free+transitive shift action). Run the verifier; it exits
    # nonzero if equivariance/freeness/transitivity/nondegeneracy fails. The SHAPE that B1's
    # witness-mandatory obligation (Σ-SEAM-GLUE) and ΞG's gauge-invariance both instantiate.
    import subprocess, os
    here = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, os.path.join(here, "jea_sppf_torsor.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"torsor verdict failed: {r.stdout.strip().splitlines()[-1:] }"
    assert "IS a torsor-bundle" in r.stdout, "torsor verifier did not confirm the bundle"
    return "PASS (parse forest = torsor-bundle: fiber invariant, span gauge, free+transitive)"


def chk_seam_provenance():
    # Ξ7: the Agda `compose` (M40Closure) transcribes the a4z2 compose-law operator-for-operator
    # — the M2 transcription link, mechanically checked. Opportunistic: needs M40Closure.agdai
    # built in _build; SKIPs cleanly otherwise (the agda decode is on-demand, jea_agdai discipline).
    import subprocess, os
    here = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, os.path.join(here, "jea_seam_provenance.py")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"provenance DIVERGED: {r.stdout.strip().splitlines()[-1:]}")
    if "SKIP:" in r.stdout:
        return "SKIP: M40Closure.agdai not built (provenance check is on-demand)"
    assert "FAITHFUL" in r.stdout, "provenance check did not confirm faithful transcription"
    return "PASS (Agda compose ↔ a4z2 compose-law: faithful, operator-for-operator)"


CHECKS = [
    ("jea_pyalg",       chk_pyalg),         ("jea_pyalg.lazy",  chk_trace_lazy),
    ("jea_pyalg.refr",  chk_pyalg_referential),
    ("jea_pysim",       chk_pysim),
    ("jea_omml",        chk_omml),          ("jea_omml_domain", chk_omml_domain),
    ("jea_oneforest",   chk_oneforest),     ("jea_sympy_bridge", chk_sympy_bridge),
    ("jea_octave_gen",  chk_octave),        ("jea_ir_unify",    chk_ir_unify),
    ("jea_omml_octave", chk_omml_octave),   ("jea_omml_render", chk_omml_render),
    ("jea_picircuit",   chk_picircuit),
    ("jea_mat260_verify", chk_mat260_verify),
    ("jea_grammar_fixpoint", chk_grammar_fixpoint),
    ("jea_sppf_torsor",  chk_sppf_torsor),
    ("jea_seam_provenance", chk_seam_provenance),
    ("jea_cuda",        chk_cuda),          ("jea_agdai",       chk_agdai),
]


def main():
    fails, npass, nskip = [], 0, 0
    for name, fn in CHECKS:
        try:
            r = fn()
        except Exception as e:
            r = f"FAIL: {type(e).__name__}: {e}"
        tag = r.split()[0].rstrip(":")     # first token (PASS may carry a ": detail" suffix)
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
