# jea/metalanguage — Δ-Π: the source-as-corpus front-end into the SPPF

Point the jea term-algebra machinery (`Wedge`/`Trace`/`recon`/hash-cons `Intern`) at **source code
and Agda interface files** instead of at a GPU eval graph. This is the **structural** successor to the
textual [`scripts/agda_similarity`](../../scripts/) — and the instrument for **cross-language
correspondence validation** (a Python `def` and an Agda proof that elaborate to the same core
structure intern to the same node id — the similarity signal textual n-grams can't see) and for the
ongoing **consolidation** effort (duplicate/shared structure is interned fan-in, computed once, read as
a lookup — never a pairwise distance matrix).

It is the **same idioms read from the Agda**, not a metric bolted on: `recon : C→C→C→C` (Agda
`Substrate.Algebra.Wedge`), the `Trace` keeps every decomposition (never-discard-residue → "similarity"
is a `trace_fold` readout, never a digest), exact `Fraction` arithmetic, hash-cons (structured node,
not a crypto-digest), and α-equivalence as exact role-lowering (names kept as residue).

## The four modules (dependency order)

| module | role | run |
|---|---|---|
| **`jea_pyalg.py`** (627L) | the base: Python `ast` → `Intern`/`Wedge`/`Trace`/`trace_fold`/`PyDivStr`/`CrossMix`. Stdlib-only. | `python jea/metalanguage/jea_pyalg.py` (self-witnesses) |
| **`jea_pysim.py`** (711L) | similarity instrument: per-unit multi-scale fingerprint = the grading; shared = interned fan-in; STRONG/PARTIAL/WEAK orbit verdict + clusters. The agda_similarity successor. | `python jea/metalanguage/jea_pysim.py <file.py> …` |
| **`jea_agdai.py`** (229L) | **third front-end** (after ast, cst): interns an Agda `.agdai` — deserializes Agda's hash-cons arena (`Agda.TypeChecking.Serialise`) into ours; arena fan-in + resolved name table. Definitional-level structure. | `python jea/metalanguage/jea_agdai.py <file.agdai> …` |
| **`jea_picircuit.py`** (360L) | the metalanguage as a **circuit operating point**: grading axes are conductances; a node's class (generator/idiom/coboundary) is where the current settles (`current_divider`, KCL — no objective minimized); axis disagreement → `<CONFOUNDED>` (the cross-term, surfaced not averaged). | `python jea/metalanguage/jea_picircuit.py <file.py> …` |

Self-contained: `jea_pyalg` (stdlib) ← `jea_pysim` ← `jea_picircuit`; `jea_pyalg` ← `jea_agdai`. No
dependency on the GPU `jea/` modules or el-atlas — same-directory imports, so run any module directly.
Verified runnable from this folder (incl. `jea_agdai` on `../agda-emit/EmitDAG.agdai`).

## Honest scope (kept visible)

- **Consolidation point with `jea_onegraph`:** `jea_picircuit` *reimplements* the onegraph Kron/Schur
  `current_divider` with `Fraction` rather than importing [`jea/jea_onegraph.py`](../jea_onegraph.py) —
  its docstring says so ("the SAME Kron/Schur jea_onegraph runs … pointed at corpus nedges instead of
  hardware conductances"). A future unification points it at the real onegraph carrier.
- **One regex** (`jea_agdai`): `re.match(rb"^[A-Za-z]…")` is a *byte-string identifier sanity filter* on
  names scavenged from the `.agdai` binary — not regex-parsing of term structure (the "no regex" charter
  targets the evaluator/term path). Replaceable by a char-class check.
- **`.agdai` decode is partial — by design:** `jea_agdai` interns the **version-stable** arena topology
  (node fan-in + the plaintext resolved-name table), NOT the per-version constructor tags. Its docstring
  carries the "WHAT IS NOT YET DECODED, AND HOW TO RECOVER IT" section — an honest, bounded front-end.

## Relationship to `scripts/agda_similarity`

`jea_pysim` is the **structural** instrument; `scripts/agda_similarity` is the **textual** one (multi-scale
n-grams over file text). They are not yet consolidated — `agda_similarity` stays as the textual baseline
until `jea_pysim` (+ `jea_agdai` for the Agda side) is validated as a superset. That consolidation is the
arc this folder was promoted to serve.
