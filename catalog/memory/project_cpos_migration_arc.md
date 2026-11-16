---
name: ""
metadata: 
  node_type: memory
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

The substrate's `Coxeter.Cyclic.Existential` already provides:

```agda
pattern c-pos k = k , c-here _
```

This is the parametric replacement for the per-Z_n legacy ladder
`c-ε` (= `c-pos zero`), `c-a` (= `c-pos (suc zero)`), `c-aa`
(= `c-pos (suc (suc zero))`), etc. The legacy declarations exist
in each of Z2/Z3/Z4/Z5/Z7-Coxeter for backwards-compatibility with
existing consumers.

The user picked Path 1 ("term-algebra as type-level source of truth")
for the polymorphic-pattern-synonym blocker. Path 1's concrete form
here is the c-pos migration: consumers stop using the legacy ladder
names and use `c-pos k` instead. Once all consumers migrate, the
legacy declarations are deletable.

**Why this matters for Python extraction:** Per `AGDA_BRIDGE.md`, the
Agda formalization and Python codec are co-developed with explicit
correspondence tables. The legacy `c-ε / c-a / c-aa / ...` ladder is
arity-dependent syntax that doesn't transfer cleanly to Python (which
just uses integer indices). The parametric `c-pos k` form maps
directly to Python's `Fin (suc n)` indices. Migration aligns the
Agda surface with the Python representation.

**Migration map**:

  Z_n.c-ε        →  (Z_n.c-pos zero)
  Z_n.c-a        →  (Z_n.c-pos (suc zero))
  Z_n.c-aa       →  (Z_n.c-pos (suc (suc zero)))
  Z_n.c-aaa      →  (Z_n.c-pos (suc (suc (suc zero))))
  Z_n.c-aaaa     →  (Z_n.c-pos (suc (suc (suc (suc zero)))))

Each migrated file needs `open import Substrate.Foundation.Fin using (zero; suc)` (or just `zero` if only c-pos zero is used).

**Status: COMPLETE (commit 9596d2e, 2026-05-22).** All 28 consumer files migrated. Per-Z_n legacy ladder (`c-ε / c-a / c-aa / c-aaa / c-aaaa / c-aaaaa / c-aaaaaa`) deleted from Z2/3/4/5/7-Coxeter. Z_n line reductions: Z2: 53 → 40, Z3: 103 → 93, Z4: 56 → 39, Z5: 56 → 39, Z7: 62 → 39 (total -80 lines from the five files). Generators / Discipline / Cardinality typecheck. `c-pos k` is the sole substrate-canonical name for "position-k canonical witness in a cyclic Coxeter group."

Key lessons from the arc:
1. Substrate had already paid the design cost (c-pos in Cyclic.Existential); the arc was 90% migration, 10% cleanup. The user's "we don't delegate enough to the term algebra" was a SHIFT IN POSTURE, not a build cost.
2. Several adjacent name spaces share the suffix `c-ε` — the Z_n PARAMETRIC pattern synonym (now gone), V₄-Coxeter's V₄-specific data constructor (stays), and CoxeterGroup's record field name (stays). Before migration the pattern-synonym clash necessitated `hiding (c-ε)` in each Z_n-Coxeter file; now the hiding can be removed because the pattern synonym is gone.
3. `git add -A` from a sub-directory of a repo with multiple roots requires care — accidentally caught `.claude/settings.json` and required a cleanup commit (b9a6ad5).

*Files migrated in commit 9596d2e (Phase A + B):*
- Substrate/Groups/Z2-Coxeter-Group.agda
- Substrate/Groups/Z3-Coxeter-Group.agda
- Substrate/Groups/Z4-Coxeter-Group.agda
- Substrate/Groups/Z5-Coxeter-Group.agda
- Substrate/Groups/Z7-Coxeter-Group.agda
- Substrate/Groups/Coxeter/GroupFromCapability.agda
- Substrate/Groups/Manifest.agda
- Substrate/Groups/Z-x-FreeCyclic-PhaseAdvance.agda
- Substrate/Groups/V4/Axioms/Lifted.agda
- Substrate/Groups/V4-Coxeter.agda
- Substrate/Groups/Actions/S3-on-V4/HomSwaps/ActHomOnCanonical.agda
- Substrate/Groups/Actions/S3-on-V4/Generators/SwapPowNormalizeEq.agda
- Substrate/Groups/Coxeter/Cyclic.agda
- Substrate/Groups/Actions/S3-on-V4/Composition/ActDotCanonical.agda
- Substrate/Groups/Actions/Z2-on-Z3/ActDot.agda
- Substrate/Groups/Capabilities/CoxeterGroup.agda
- Substrate/Groups/V4/Bijection.agda
- Substrate/Groups/Actions/S3-on-V4/Axioms/ActEpsilonN.agda
- (and ~5 others — re-run the grep below to refresh the list)

Refresh command:
  `grep -rln "\bc-ε\b\|\bc-a\b\|\bc-aa\b\|\bc-aaa\b\|\bc-aaaa\b" Substrate/ --include="*.agda" | grep -v "Z[0-9]*-Coxeter.agda$" | grep -v "Cyclic/Existential.agda$"`

**Final cleanup (DONE in 9596d2e):**
1. ✅ Deleted `pattern c-ε = ...` through `pattern c-aaaaaa = ...` declarations from each of Z2/Z3/Z4/Z5/Z7-Coxeter.
2. ✅ Deleted per-Z_n `canonical-cover` from Z2/Z4/Z5/Z7 (no internal users). Z3 retains `canonical-cover` (internal user: inv-distrib-canonical) but rewritten to pattern-match via `c-pos` instead of the legacy ladder.
3. ✅ Generators / Discipline / Cardinality typecheck.

**Permanent surface:** `c-pos k` (k : Fin (suc n)) is the canonical position-k witness across all Z_n. Consumers use either `Z_n.c-pos k` (qualified) or `c-pos k` (after `open Z_n`).

See also: [[project-cluster-to-action-analysis-2026-05]], [[project-term-algebra-extension]].
