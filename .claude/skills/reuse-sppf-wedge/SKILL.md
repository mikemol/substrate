---
name: reuse-sppf-wedge
description: >-
  Fire this BEFORE writing a new def/helper/module/bridge in this repo, BEFORE
  consolidating/deduping/lifting code, and the instant you catch yourself calling
  shared structure "AST floor" / "legitimately-kept residue" / "structurally
  divergent" or reading a STRONG/WEAK/percentage similarity number. The substrate
  interns BOTH its Agda AND its Python into content-addressed SPPFs and exposes a
  set-relational WEDGE (∩ shared + the two residues + a subset/consolidation
  verdict) over them — this skill says which tool interns which corpus, how to run
  it, and how to read the wedge instead of collapsing to a scalar. It exists
  because the actor repeatedly (a) claimed "no python internment / no wedge on .py"
  (categorically false), (b) dismissed real shared subtrees as floor without
  running the enumeration, and (c) read the discarded percentage verdict.
---

# Reuse via the SPPF wedge (find it, run it, read it)

The substrate content-addresses its own source — Agda **and** Python — into shared-packed
parse-forests, and exposes the **wedge** `a = recon q b r` over them: for two units it reports
the shared support ∩ (the reuse), the two residues (what each side carries beyond the other), and
a **verdict** (instantiate / generalize / verbatim / factor · DUP / CONSOLIDATED / MIXED) — never a
similarity percentage. Before you build, consolidate, or declare something "floor," you run this and
read the wedge.

## When this fires

- **Before writing a new `def`/helper/record/module/bridge** — the reuse-search trigger from CLAUDE.md,
  now mechanical: lower the proposal into the corpus and read its nearest kin.
- **When consolidating / deduping / lifting** a shared skeleton (the parallel-construct → dedup-lift move).
- **On your own tells:** "this is AST floor", "legitimately-kept residue", "structurally divergent",
  "WEAK/PARTIAL/STRONG orbit", "68% shared", "these are distinct routines" — every one of these is either
  the *collapse-to-scalar* the tooling deliberately removed, or the *assume-floor* reflex the sweep exists
  to disprove. Stop and run the enumeration.
- **A circular import between two of your files IS a dedup smell** — two tools reaching into each other for a
  shared helper. Lift the ∩ to a single-source module; the cycle breaks by construction.

## The two corpora (this is the fact I kept getting wrong)

| corpus | interned by | persisted? |
|---|---|---|
| **Python `.py`** | `jea_pyalg.py` (`Intern`/`Lowerer`/`lower_source`) → `jea_pysim.Corpus.add_file` (`jea_pysim.py:105`) | **in-memory only** — there is NO python `catalog.db`; `jea_pysim --persist` drops non-`.agdai` inputs (`jea_pysim.py:888`) |
| **Agda `.agdai`** | `sppf_db.py` (`decode_core`) → `catalog/catalog.db` (built by `reuse_catalog.py`, `gen_catalog.py`) | **yes** — `catalog.db` (structs/node/unit/`shared_subtree`), Agda-only |

Python internment is real and lives in-memory inside a `Corpus`; the reuse/wedge query over it is a set
operation on interned support, not a SQL query. "No python internment into SPPFs" is **categorically false.**

## The tool map — which tool for which corpus

**PYTHON — the propose→nearest WEDGE (use this before writing a helper, or to check code you just wrote):**
```
scripts/reuse_check.py --propose <file.py> --against 'scratch/*.py' 'jea/metalanguage/*.py' --top 8
```
Interns `--against` as the reference corpus, then interns each `def` in `--propose` and reports, per existing
def: `∩` (shared support = reuse) · `+prop` (Sₚ∖Sₑ) · `+exist` (Sₑ∖Sₚ) · **verdict** — `IDENTICAL` (reuse
verbatim) · `PROPOSAL ⊆` (instantiate the existing) · `EXISTING ⊆` (generalize it) · `OVERLAP` (factor the
shared core, each keeps its residue) · `NOVEL` (∩=∅ everywhere) (`reuse_check.py:82-111`). The scalar
"0.32/WEAK" was **explicitly removed** here (`reuse_check.py:10-15`, [[dont-collapse-to-smallest-representable]]).
This is the `.py`-capable twin of `reuse_sweep`. To sweep a whole file, propose it against its siblings.

**PYTHON — enumerate every shared subtree (the "assume-floor" killer):**
```
scripts/membudget run 2048 lbl -- python3 jea/metalanguage/jea_pysim.py <files.py> --clusters --extract --recursive --min-fanin 2 --min-size 2
```
`--extract` = parametric-helper candidates (shared subtree in ≥2 units = a consolidation target: parameterize
it, the instances consolidate onto it). `--recursive` = shared structure INSIDE the residue. `--skeleton` =
typeholed clusters (shared skeleton + typed holes = the symmetric difference). `--min-size 2` **enumerates
all** — no threshold, because fanin IS duplication, not noise. ⚠ **IGNORE the `verdict: STRONG/PARTIAL/WEAK
(NN% max shared)` line** — that scalar is the collapse this whole family removed; it's still shipped from
`jea_pysim.py:524-532,721-738` but was superseded in narrative by the S(g) shape (`jea_pysim.py:202-352`).
Read the enumerated subtrees + the S(g) cliff class, never the %.

**PYTHON — consolidation templates (anti-unification):** `autocorr_synth.py` (`E.templatize`), `jea_extrude_ir.py`
(`Extruder`/`extrude`) — emit one abstraction + per-instance fillings for a cluster.

**AGDA — changed-code wedge (the pre-commit gate):**
```
scripts/reuse_sweep.py [--gate]        # git-changed .agda vs catalog.db; DUP/CONSOLIDATED/MIXED
```
Agda-ONLY by construction (`git_changed` filters `.agda` `reuse_sweep.py:33`; `module_of` is relative to
`agda/` `:27`; reads Agda-only `catalog.db` `:40-50`). Wired advisory in `.githooks/pre-commit` (`|| true`,
guarded by `[ -f catalog.db ]`). Do NOT pass it `.py` — it will silently find nothing. For `.py`, use
`reuse_check.py`.

**AGDA — interactive / SQL:** `reuse_tui.py` (`db_rows` SPPF walk + `resolve_orbit` verdict + the coset
**residue** rendered as a Coxeter word, `reuse_tui.py:226-304`); `sppf_query.py reuse` (DUP/CONSOLIDATED/MIXED
as SQL, `sppf_query.py:64-87`).

**THE PER-NODE WEDGE (the algebra underneath):** `jea_pyalg.Wedge`/`recon`/`trace` (`a = recon q b r`, witness
carried, `jea_pyalg.py:92-188`) and `CrossMix.cross_term` (two nodes' subterm support → shared/only_a/only_b/
degree, `jea_pyalg.py:665-687`). The corpus-level wedges are built on these.

## How to READ the wedge (not the percentage)

For a proposal vs an existing def:
- **∩ (shared)** — the structure already exists; this is what you REUSE.
- **+prop (Sₚ∖Sₑ)** — what your proposal genuinely ADDS (its residue).
- **+exist (Sₑ∖Sₚ)** — what the existing def carries beyond you.
- **verdict** decides the MOVE: `IDENTICAL`→delete yours, call theirs · `PROPOSAL⊆`→instantiate theirs ·
  `EXISTING⊆`→generalize theirs to cover you · `OVERLAP`→lift the ∩ to a single-source, each keeps its residue
  (the symmetric difference) · `NOVEL`→genuinely new.

`OVERLAP` is not "no action" — it is *factor the shared core*. That is the lift. The residues are what you keep
per-side, not an excuse to leave the duplicate.

## The two anti-patterns this skill kills

1. **Collapse-to-scalar.** Reading "WEAK/49.7%/PARTIAL orbit" and concluding "distinct routines, nothing to do."
   That number is the discarded verdict. Read the ∩ + residues + subset-verdict, or the enumerated subtrees.
2. **Assume-floor.** Labeling a size-8 shared subtree "AST floor" / "legitimate residue" WITHOUT running the
   enumeration and looking at what the subtree IS. "When the sweep tool was introduced, it identified that a lot
   of things assumed-floor were not in fact floor." Examine each candidate: a genuine lift (the paren-depth walk
   shared by two helpers → one `_depth_iter`) vs a stdlib-primitive call whose varying argument is the whole
   content (`re.search(<literal>, x)` → wrapping consolidates nothing). Decide per-candidate by looking, never by
   size-label.

## Honest boundaries

- `reuse_check.py` interns a not-yet-committed proposal; for an Agda proposal it needs a COMPILED `.agdai`
  (typecheck first). It is NOT hook-wired — it is a manual query you run.
- The persisted SPPF (`catalog.db`) is Agda-only; python reuse is in-memory (rebuilt per invocation). There is no
  python `--persist` path (`jea_pysim.py:888`).
- `jea_pysim`'s STRONG/WEAK verdict is dead weight still emitted; the removal is complete in `reuse_check.py`,
  partial in `jea_pysim.py`. Trust `reuse_check.py`'s wedge; ignore `jea_pysim`'s percentage.
- Always run heavy interns under `scripts/membudget` ([[feedback_always_membudget]]).
