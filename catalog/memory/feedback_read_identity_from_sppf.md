---
name: feedback_read_identity_from_sppf
description: "the substrate interns its code into a content-addressed SPPF — read identity/relation OUT of it (support-equality, the wedge), never a proxy (floor-guess / percentage / string-ast compare / byte-baseline / \"no python wedge\")"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

The substrate interns BOTH its Agda (`.agdai` → `catalog.db` via `sppf_db`) AND its Python (`.py` → in-memory
via `jea_pyalg`/`jea_pysim.Corpus.add_file`) into a content-addressed SPPF. That interned structure IS the
identity/relation oracle. When deciding "are these the same def / do these share structure / is this reuse" —
**intern into the SPPF and read the answer OUT of it**, never a proxy.

The tools and how to read them (see the `reuse-sppf-wedge` skill for the full map):
- PY def identity / nearest kin: `reuse_check.py --propose <f.py> --against …` → the WEDGE (∩ shared + Sₚ∖Sₑ +
  Sₑ∖Sₚ + IDENTICAL·⊆·⊇·OVERLAP verdict). `jea_pysim` support-set EQUALITY in one Corpus = "same def".
- PY enumerate every shared subtree: `jea_pysim … --extract --recursive --min-size 2` (no threshold).
- AGDA changed-code: `reuse_sweep.py --gate`; interactive `reuse_tui`; SQL `sppf_query reuse`.

**Why:** across one session I repeatedly substituted a PROXY for the SPPF's ground truth, each caught by the
user: (a) called a shared subtree "AST floor / legitimately-kept residue" WITHOUT enumerating (assume-floor —
"what the sweep disproves"); (b) read the STRONG/WEAK/`49.7%` scalar — the collapse-to-smallest we DELETED from
reuse_check; (c) verified def-identity with a whitespace-strip then `ast.dump` — both MISS alpha-renamed locals
that the SPPF quotients (reinvent-the-equivalence); (d) gated on a byte-identical baseline of output that was
NON-DETERMINISTIC (PYTHONHASHSEED unset — set-identity was the real gate); (e) asserted "no python internment
into SPPFs / no wedge on .py" — CATEGORICALLY FALSE. Each proxy FLATTENS the interned structure; the SPPF
already holds the answer. This is construct-dont-classify meta-substitution #5 (flatten/rebuild-the-given vs
read-the-structure-that's-already-there), and it is the mission's own thesis — proven by dogfooding the dedup on
the tooling itself (scripts/ → pure-def fixpoint, 0 IDENTICAL families, rung-0 leaves ⊏ rung-1 ShredGraph).

**How to apply:** the tells are "floor / legitimate residue / structurally divergent / WEAK / NN% shared / let
me string-compare / byte-identical baseline / there's no python wedge." On any of them — stop, intern into the
SPPF, read the wedge (∩ + the two residues + the subset verdict) or the support-equality, and MEASURE what's
achievable (test determinism before byte-gating). Mechanize the lift and verify identity via the SPPF's OWN
equivalence, never a hand-rolled one. Widens [[read-structure-dont-rebuild]] and
[[dont-collapse-to-smallest-representable]]; the recurring-non-determinism half relates to [[reread-meters-toctou]].
