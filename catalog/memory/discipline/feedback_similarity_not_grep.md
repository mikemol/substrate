---
name: similarity-not-grep
description: "For \"find shape-equivalent code\" questions in the substrate, use the structural similarity instrument jea/metalanguage/jea_pysim.py (over .py AND Agda .agdai core) — agda_similarity is RETIRED; grep misses inline lambdas / equivalent helpers."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

When the question is "are there OTHER sites with the same SHAPE as X" (for extraction-candidate analysis, cohort discovery, post-extraction sweeps), the substrate-canonical tool is the structural similarity instrument, NOT grep.

**PROACTIVE trigger (Ε(b)/G9, 2026-06-21):** the search fires not only POST-hoc but BEFORE building — when a plan PROPOSES new machinery (a new def/lemma/module/bridge), that proposal IS the trigger to search for the structure it would reinvent. The substrate is dense; most "build X" is "instantiate the X that already exists." One arc ran 5 near-reinventions caught only by user pointers / late grounding (recip lemmas vs the Ⓖ★ cross-mixer dual; bespoke factorisation vs the div-mod wedge; a Bézout reproof vs `euclid`; a Monoid→Category bridge vs `deloop`; a round-trip Canonical vs `split-Canonical`). Escalated off this recalled-memory layer: CLAUDE.md §"Reuse-search BEFORE building new machinery" (always-loaded) is the standing form; the `construct-dont-classify` skill carries the "reinvent-vs-reuse" reflex when its file can be edited. Also scan `Substrate.Generators`, the `*.Registry` bridge-indexes, and the apex memories [[project_split_idempotent_apex]] / [[project_witness_tower_constructive_generator]] for the generator to instantiate.

**UPDATED 2026-06-18:** `scripts/agda_similarity` (the textual multi-scale n-gram tool) was RETIRED in commit b20a1d2 — "subsumed by jea_pysim+jea_agdai (Π3 CLOSED)". Only stale `.pyc` bytecode remains under `scripts/agda_similarity/__pycache__/` (source deleted, recoverable via git at b20a1d2^). The LIVE tools:
- `jea/metalanguage/jea_pysim.py` — the similarity instrument. Works STRUCTURALLY via the term-algebra interner (jea_pyalg) over BOTH Python AST and Agda core (pass a `foo.agdai`), not regex. Similarity is a READOUT of the interned SPPF (fan-in computed once at intern, no pairwise distance matrix) — itself a never-discard-residue instance. Modes: `--clusters` (unit cohorts by shared high-fan-in subtrees), `--extract` (parametric-helper candidates), `--skeleton` (parametric template), `--shape`, `--recursive`, `--metalanguage`, `--json`. Orbit verdict STRONG≥0.80 / PARTIAL≥0.50 (same thresholds as the retired tool's `score`). Knobs: `--min-shared 0.6 --min-size 6 --min-cohesion 0.5 --min-fanin 3`.
- `jea/metalanguage/jea_agdai.py` — the .agdai front-end (Haskell `agdai_shim` decodes Agda's compiled interface) feeding the same SPPF; def-level semantic structure, not surface text.

**Why structural, not grep:** grep matches literal text and MISSES shape-equivalent sites using inline lambdas `λ i → …`, helper functions passed as arguments, or differently-named where-bindings. The interner lowers all front-ends into one forest; shared canonical nodes = corroborated shape.

**How to apply:** `python jea/metalanguage/jea_pysim.py <files-or-.agdai globs> --clusters --extract --skeleton` — for Agda, point at the compiled `.agdai` under `agda/_build/.../Substrate/...`. Strict thresholds first, loosen if zero clusters.

**Reason for keeping this rule:** at one point I used the Explore agent to grep for hand-written `agree-on-basis` where-clauses after a 4-site fin-cover refactor; user pointed out I should have used agda_similarity. The Explore agent reported "zero other sites" — which was textually accurate but methodologically wrong (it can't see shape-equivalent inline lambdas). The similarity script gives shape-equivalent results across surface variations.

See [[project-cluster-action-methodology]] for how cluster output drives extraction verdicts; [[project-cluster-to-action-analysis-2026-05]] for the prior arc's worked examples.
