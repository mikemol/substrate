---
name: project_punctured_fin_primitive
description: Fin.Punctured + Axes.Punctured (punchIn/punchOut bijection) landed green with Cardinality as real consumer; Stab-S3 wiring attempted+reverted (breaks definitional round-trips in Iso/Hom)
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

The punctured-finite-set bijection `Fin (suc n) ∖ {k} ≅ Fin n` as the
named generic for the substrate's hand-enumerated "skip one element"
bijections. All --safe --without-K, zero postulates, verified standalone.

**Landed (green):**
- `agda/Substrate/Foundation/Fin/Punctured.agda` — `punchIn`, `punchIn-≢`,
  `punchOut` (impossible diagonal via ⊥-elim, NO DecEq), `punchOut-irrelevant`,
  `punchOut-cong`, `punchOut-punchIn`, `punchIn-punchOut`. Carrier-generic.
- `agda/Substrate/Axes/Punctured.agda` — Axis-layer instance: the canonical
  `axis-↔-fin4` (now SINGLE SOURCE OF TRUTH) + the anchor-skipping bridge
  (`axis-punchIn`/`axis-punchOut` + round-trips) transported along it.
- `Cardinality.agda` — REAL CONSUMER: its private `axis-↔-fin4` copy deleted,
  now `open import Axes.Punctured public using (axis-↔-fin4)` (public so
  Cardinality.Product, which imports it from Cardinality, is unaffected).
  This demonstrates the multi-consumer/dedup leg, not just the pedagogical leg.

**Attempted + REVERTED — the refl→transport tradeoff, made concrete:**
Rewiring `Stab-S3`'s bridge pair (`fin3-to-non-anchor`/`non-anchor-to-fin3`)
to alias axis-punchIn/Out type-checked in Stab-S3 itself and in 4/6
consumers, but BROKE `Stab-S3-Iso` + `Stab-S3-Hom` (and `S4Iso-Bridges`,
which imports Iso): those prove round-trips by `refl` on concrete anchors
(`fin3-non-anchor-fin3 D (SFin.apply s zero)` etc.), which needs the bridge
to reduce DEFINITIONALLY. The transported punchOut does not reduce, so the
`refl`s fail (UnsolvedConstraints on the ≢-witness). Reverted to the green
`lookup`-based form; Stab-S3 now carries a NOTE pointing at the primitive +
why migration is deferred. The user explicitly wanted this attempted ("if
it means more explicit fluidity structure it may be worth it"), and the
empirical answer is: worth it for Cardinality (clean), not yet for Stab-S3
(36+ consumer cases need subst-based round-trips first).

KEY LESSON (validated): definitional `refl` round-trips on concrete finite
data are an evaluation coincidence that downstream proofs silently bank;
replacing the map with a transported/abstract one converts those into
subst obligations the consumers don't yet discharge. Whether that bites is
EMPIRICAL (grep the consumers) — here it bit exactly the 2 consumers that
pattern-match anchors. See [[feedback_common_substructure_recursively]],
[[feedback_fine_grained_over_coarse]].

**FOLLOW-UP (scoped):** migrate Stab-S3-Iso/-Hom round-trips to subst-based
(via axis-punchOut-punchIn / non-anchor-to-fin3-cong), THEN re-point
Stab-S3's bridge at Axes.Punctured. Until then both forms coexist: the
generic primitive (with Cardinality consumer) and Stab-S3's definitional
lookup form. Related: [[project_deliverable_scan_2026_06]].
