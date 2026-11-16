---
name: level-poly-record-is-set1-paydown
description: "Making a fixed-Setₙ record level-polymorphic drops it from the Set₁ ratchet — the poly codomain sort is uncounted (polymorphism admitted, not held)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Turning a record pinned to a FIXED `Set₁` (e.g. `record R (Obj : Set₁) (Hom : Obj→Obj→Set₁) : Set₁`) into a
LEVEL-POLYMORPHIC one — `record R {ℓ₀ ℓ₁ : Level} (Obj : Set ℓ₀) (Hom : Obj→Obj→Set ℓ₁) : Set (ℓ₀ ⊔ ℓ₁)` —
is itself a Set₁ RATCHET PAYDOWN, not merely an enabler. `set1_ratchet_cores.py` counts a def iff its peeled
codomain sort is `Type` at a CLOSED level ≥ 1; a poly `Set (ℓ₀ ⊔ ℓ₁)` quantified over `{ℓ : Level}` is not a
closed ≥1 level, so the record + its generated helpers stop counting. Measured: level-poly-ing `UPCategory`
alone paid down −7 (⟡ta-upterm, 2026-07-15).

**Why:** polymorphism over a universe level is admitted under `--safe` and is NOT a held object — it is
[[set1-is-grade-collapse]] ("construct across the grade, don't hold the family") realized at the universe
level. The fixed `Set₁` WAS the collapse; the poly form is the every-grade form. Confirmed earlier in the
plan: "a ∀{C : ℕ→Set} UP theorem has a large TYPE (Set₁) — that is polymorphism, admitted, NOT a held object."

**How to apply:** when a record is pinned `Set₁` only to accept Set₁ object/hom families, make it
level-polymorphic instead of hunting a Set₀ carrier — it accepts BOTH the Set₀ instance and the old Set₁
families, is backward-compatible when nothing annotates its level (verify: consumers only APPLY it, don't
annotate its sort), AND pays down the ratchet for free. Relates to [[set1-carrier-always-parameterize]],
[[set1-is-grade-collapse]].
