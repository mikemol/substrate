---
name: feedback_bijection_parallel_false_positive
description: "The bijection shape-parallel (record {to,from,to-from,from-to} ×5) is AUDITED false-positive-for-collapse: 3 are load-bearing setoid/extensional isos, 2 are scoped propositional generics — do not re-attempt to collapse."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**Ⓒ.bijection audit (2026-07-05): the `record {to,from,to-from,from-to}` ×5 shape-parallel is a
FALSE POSITIVE for collapse.** The reuse-index/catalog fingerprint is member-NAME based, not
type-aware, so it groups five records that share field *names* but differ in the *types* of the
round-trip laws. Do not re-open this as a dedup target; the split is:

**3 load-bearing setoid/extensional isos — LEAVE (their authors documented why they can't use
`_↔_`):**
- `Groups.Stab-S3-Iso.Stab≃S₃` — round-trips up to `apply`-agreement (`SFin.apply (to (from s)) i ≡
  SFin.apply s i`), not `to (from s) ≡ s`.
- `Cocycles.V4Signature.S4Iso.TotalSpace≃S₄` — `to-from` up to a setoid `≈`, `from-to` up to `≡`
  (HETEROGENEOUS); its comment: "Cannot use stdlib's `_↔_` (= Inverse on propositional setoids)".
- `Cocycles.V4Signature.Codeword.LiveS4Bijection.Live≃Permutation` — comment: "stdlib's `_↔_` wants
  `_≡_` on both sides; [ours doesn't]".
The propositional bijection `to (from b) ≡ b` STRUCTURALLY can't express these; collapsing would
destroy the load-bearing equality relation. This is the [[feedback_dedup_preserve_crossdomain_bridges]]
"read the actual defs, not the fingerprint" rule — an IDENTICAL member-name hit with DIFFERENT field
types is a distinction, not a redundancy.

**2 propositional generics — RELATED-not-merged (cross-referenced in-code, not collapsed):**
`Algebra.Bijection._↔_` (Set₀, stdlib-compatible, richer combinators mk↔ₛ′/↔-sym/↔-trans/_×-↔_, 7
dependents) and `Foundations.Bijection.Bijection` (universe-polymorphic, product combinator, 3
dependents). Same concept; `_↔_ A B` = `Bijection {lzero} A B`. NOT merged: each has its own
combinator suite + dependent set, so merging is a real 7-dependent migration for ~5 lines — low
value, moderate risk. Instead their headers now cross-reference each other + this memory (resolves
the "which bijection do I use?" discoverability debt without churn).

**The true common center does NOT exist** (reuse-searched: only `Algebra.Setoid`, `Setoid.Map`,
categorical `Category.Iso.IsIso`, and domain isos `WedgeIso`/`LinearBijection`/… with different
shapes — no generic setoid-bijection). A HETEROGENEOUS setoid-bijection (bijection up to a per-side
equivalence `_≈A_`, `_≈B_`, of which `_↔_` is the (≡,≡) case and the 3 specifics are other instances)
would unify all five — but that is a BUILD arc (`Ⓒ.setoid-bij`), warranted only if the count grows,
not a fold-in. Related: [[feedback_reuse_search_before_feasibility_conclusions]].
