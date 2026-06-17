# jea/metalanguage — Δ-Π: the source-as-corpus front-end into the SPPF

Point the jea term-algebra machinery (`Wedge`/`Trace`/`recon`/hash-cons `Intern`) at **source code
and Agda interface files** instead of at a GPU eval graph. This is the **structural** successor to the
textual `scripts/agda_similarity` (now retired — see below) — and the instrument for **cross-language
correspondence validation** (a Python `def` and an Agda proof that elaborate to the same core
structure intern to the same node id — the similarity signal textual n-grams can't see) and for the
ongoing **consolidation** effort (duplicate/shared structure is interned fan-in, computed once, read as
a lookup — never a pairwise distance matrix).

It is the **same idioms read from the Agda**, not a metric bolted on: `recon : C→C→C→C` (Agda
`Substrate.Algebra.Wedge`), the `Trace` keeps every decomposition (never-discard-residue → "similarity"
is a `trace_fold` readout, never a digest), exact `Fraction` arithmetic, hash-cons (structured node,
not a crypto-digest), and α-equivalence as exact role-lowering (names kept as residue).

## The Σ apparatus — front-ends lower into ONE forest; readouts are CrossMix consumers

Everything below interns into the same `jea_pyalg.Intern`. **Front-ends** turn a language into forest IR;
**readouts** compare/classify over the forest; the **sympy hub** fans one bridge out to N generation
targets. The recursive law: a language is a *coordinate*, the forest is the *geometry*, the cross-term is
comparison-in-the-geometry ("does the Octave realize the Agda proof?" = same geometry, different coordinate).

```text
 Python  Agda-core  CUDA   OMML        sympy
  (ast)  (.agdai)  (.cu)  (m:func…)   (Expr)
    └────────┴────────┴──────┴───────────┘
                  ONE interned forest  (jea_pyalg: Intern/Wedge/Trace/CrossMix)
        ┌───────────────┼────────────────────────────┐
   jea_oneforest   jea_omml_domain        jea_sympy_bridge ──→ octave / latex / mathml / ccode
   (cross-arm      (audience carrier:     (the HUB: build one bridge,
    verify gate)    expose the fork)       inherit N printers)
```

| module | kind | role |
|---|---|---|
| **`jea_pyalg.py`** | base | Python `ast` → `Intern`/`Wedge`/`Trace`/`trace_fold`/`PyDivStr`/`CrossMix`. Stdlib-only; every other module interns into its `Intern`. |
| **`jea_pysim.py`** | readout | structural similarity (the retired `agda_similarity`'s successor): S(g) SHAPE + clusters + `--shape` consolidation scan over the SPPF. Reads `.py` AND `.agdai` (via `jea_agdai`). |
| **`jea_agdai.py`** (+ `agdai_shim.hs`) | front-end | Agda `.agdai` → core IR. `agdai_shim` (ghc `-package Agda`) decodes via Agda 2.8.0's own deserialiser and walks each def's type + clause bodies; `core_intern_agdai` interns the FULL child-edge DAG (Φ4). |
| **`jea_cuda.py`** | front-end | CUDA ⇄ IR as ONE bidirectional grammar (`lower_cuda`/`project_cuda` + `fixpoint_test`); memory-space = a `Space` carrier. Needs libclang. |
| **`jea_omml.py`** | front-end | OMML (`<m:func>`/`m:d`/`m:sSub`/operator runs) → IR. `m:func`=explicit App (no fork); juxtaposition → a tagged ADJACENCY partition. Grounded in mat260's vocabulary. |
| **`jea_picircuit.py`** | readout | the metalanguage as a circuit operating point (grading axes = conductances; class = where current settles, KCL). |
| **`jea_oneforest.py`** *(in `jea/`)* | readout | Σ-FOREST: the cross-arm verification gate — `cross_term` across source/core/kernel arms = "does the artifact realize the proven core?" (degree 0 = realizes). |
| **`jea_omml_domain.py`** *(in `jea/`)* | readout | the audience-domain carrier: a partial map that commits an OMML partition's strand only where it has authority (silence = identity; domains form a monoid under override). |
| **`jea_sympy_bridge.py`** | hub | bidirectional forest⇄sympy (assumptions = carrier-selections; fixpoint retraction). The HUB: `project_*` → sympy → its own canonical printers. |
| **`jea_ir_unify.py`** | hub | ONE structured forest-IR both dialects share; `project_unified` reads OMML `BinOp` (k=2) AND sympy n-ary `Op` — the translator `omml_ir_to_sympy` retired into it. |
| **`jea_octave_gen.py`** | fan-out | forest → sympy → Octave `.m` (stands on `sympy.codegen`); octave→matlab is a user `translator` hook, not reimplemented. |
| **`jea_omml_octave.py`** | pipeline | end-to-end OMML → sympy → Octave `.m` (+ LaTeX), via `jea_ir_unify.project_unified`. Validated 12/12 on the mat260 cipher corpus. |
| **`jea_metalanguage_gate.py`** | gate (Σ6) | the regression net: asserts each instrument's structural invariant; pure modules run, toolchain ones self-skip. Fired per-commit by `.githooks/pre-commit` on staged `jea/metalanguage/` (+ the two root Σ modules). |

Self-contained (same-directory imports; no dependency on the GPU `jea/` modules or el-atlas). Pure modules
need only stdlib + sympy; `jea_cuda` needs libclang, `jea_agdai`/`agdai_shim` need ghc + Agda 2.8.0.

## Honest scope (kept visible)

- **Consolidation point with `jea_onegraph`:** `jea_picircuit` *reimplements* the onegraph Kron/Schur
  `current_divider` with `Fraction` rather than importing [`jea/jea_onegraph.py`](../jea_onegraph.py) —
  its docstring says so ("the SAME Kron/Schur jea_onegraph runs … pointed at corpus nedges instead of
  hardware conductances"). A future unification points it at the real onegraph carrier.
- **One regex** (`jea_agdai`): `re.match(rb"^[A-Za-z]…")` is a *byte-string identifier sanity filter* on
  names scavenged from the `.agdai` binary — not regex-parsing of term structure (the "no regex" charter
  targets the evaluator/term path). Replaceable by a char-class check.
- **`.agdai` decode — now FULL via the shim (Φ4):** `jea_agdai` has two paths: `intern_agdai` (the
  toolchain-free fan-in signature — version-stable arena topology + name table) and `core_intern_agdai`,
  which drives `agdai_shim.hs` (ghc `-package Agda`, Agda 2.8.0's own deserialiser) to intern the FULL
  child-edge core DAG (type + clause bodies). The shim binary is gitignored; the `.hs` source is tracked.

## Subsumed `scripts/agda_similarity` (retired)

`scripts/agda_similarity` (textual, multi-scale n-grams over file text) was **retired** once `jea_pysim`
(structural, over the interned SPPF) + `jea_agdai` (Agda `.agdai` core via `agdai_shim`) covered both its
languages: Python AST and Agda core. The structural tool is strictly better — exact α-equivalence (not regex
anonymisation), the S(g) SHAPE (not a max-collapse scalar), cross-file hole-localised candidates — and now
ingests `.agda` interfaces too (`jea_pysim foo.agdai`, walking type + clause bodies). The one thing the
textual tool did that this does not: compare *unbuilt* `.agda` source text (the structural path needs the
built `.agdai`). That consolidation is the arc this folder was promoted to serve; it is complete.
