------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Mode
--
-- Slice 2 of the shadow-architecture arc (Shadow E). The four prior
-- moves named in the document — `decomposable-by-entailment`,
-- `snap-to-grid`, `regroup-from-shadows`, `mediation-guard` — as
-- subsets of the seven Fano lines. From Increment 6:
--
--                       L₁    L₂    L₃    L₄    L₅    L₆    L₇
--      decomp           ✓                 ✓
--      snap                               ✓     ✓                 (read-only)
--      regroup                                  ✓           ✓
--      guard                  ✓     ✓                 ✓
--
-- The covering claim (every Fano line lies in at least one mode's
-- territory) is `coverage`. The four sub-claims —
--
--   * L₁ uniquely decomp
--   * L₇ uniquely regroup
--   * {L₂, L₃, L₆} uniquely guard (= the star of 001)
--   * L₄, L₅ are shared (decomp/regroup write; snap reads)
--
-- — are also stated explicitly. The warning at the end of Increment 6
-- (re-instantiating the modes as separate skills loses the cross-mode
-- entailments at L₄/L₅) is the operational reason these subsets must
-- be defined over the same underlying Line type.
--
-- The guard's full star = star-of-001: the three Fano lines through
-- the point e₃ = p₀₀₁ are exactly {L₂, L₃, L₆}. Surfaced as
-- `guard-territory-is-star-001`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Mode where

open import Substrate.Foundation.Bool using (Bool; true; false; _∨_; T)
open import Substrate.Foundation.Sum using (inj₁; inj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.SelfReference using (_on_)

------------------------------------------------------------------------
-- 1. The four modes.
------------------------------------------------------------------------

data Mode : Set where
  decomp  : Mode
  snap    : Mode
  regroup : Mode
  guard   : Mode

------------------------------------------------------------------------
-- 2. Mode territory: which lines does each mode operate on?
--
-- Enumerated explicitly (7 cases per mode) so that all coverage,
-- uniqueness, and sharing facts reduce by `refl`.
------------------------------------------------------------------------

in-mode : Mode → Line → Bool

-- decomp: L₁ unique, L₄ shared with snap.
in-mode decomp L₁ = true
in-mode decomp L₂ = false
in-mode decomp L₃ = false
in-mode decomp L₄ = true
in-mode decomp L₅ = false
in-mode decomp L₆ = false
in-mode decomp L₇ = false

-- snap: L₄ shared with decomp, L₅ shared with regroup. Read-only —
-- the snap mode reads the line states; it does not write them.
in-mode snap L₁ = false
in-mode snap L₂ = false
in-mode snap L₃ = false
in-mode snap L₄ = true
in-mode snap L₅ = true
in-mode snap L₆ = false
in-mode snap L₇ = false

-- regroup: L₅ shared with snap, L₇ unique.
in-mode regroup L₁ = false
in-mode regroup L₂ = false
in-mode regroup L₃ = false
in-mode regroup L₄ = false
in-mode regroup L₅ = true
in-mode regroup L₆ = false
in-mode regroup L₇ = true

-- guard: full star of 001 — exactly the three lines through e₃.
in-mode guard L₁ = false
in-mode guard L₂ = true
in-mode guard L₃ = true
in-mode guard L₄ = false
in-mode guard L₅ = false
in-mode guard L₆ = true
in-mode guard L₇ = false

------------------------------------------------------------------------
-- 3. Coverage: every line lies in at least one mode's territory.
------------------------------------------------------------------------

covered : Line → Bool
covered ℓ = in-mode decomp ℓ ∨ in-mode snap ℓ ∨ in-mode regroup ℓ ∨ in-mode guard ℓ

coverage : ∀ (ℓ : Line) → covered ℓ ≡ true
coverage L₁ = refl
coverage L₂ = refl
coverage L₃ = refl
coverage L₄ = refl
coverage L₅ = refl
coverage L₆ = refl
coverage L₇ = refl

------------------------------------------------------------------------
-- 4. Uniqueness: L₁ is exclusive to decomp; L₇ is exclusive to
-- regroup. Each "exclusive" claim is the conjunction of one
-- positive and three negative facts.
------------------------------------------------------------------------

L₁-decomp-only-1 : in-mode decomp L₁ ≡ true
L₁-decomp-only-1 = refl
L₁-decomp-only-2 : in-mode snap L₁ ≡ false
L₁-decomp-only-2 = refl
L₁-decomp-only-3 : in-mode regroup L₁ ≡ false
L₁-decomp-only-3 = refl
L₁-decomp-only-4 : in-mode guard L₁ ≡ false
L₁-decomp-only-4 = refl

L₇-regroup-only-1 : in-mode regroup L₇ ≡ true
L₇-regroup-only-1 = refl
L₇-regroup-only-2 : in-mode decomp L₇ ≡ false
L₇-regroup-only-2 = refl
L₇-regroup-only-3 : in-mode snap L₇ ≡ false
L₇-regroup-only-3 = refl
L₇-regroup-only-4 : in-mode guard L₇ ≡ false
L₇-regroup-only-4 = refl

------------------------------------------------------------------------
-- 5. Sharing: L₄ is shared decomp + snap; L₅ is shared snap + regroup.
------------------------------------------------------------------------

L₄-decomp : in-mode decomp L₄ ≡ true
L₄-decomp = refl
L₄-snap : in-mode snap L₄ ≡ true
L₄-snap = refl
L₄-not-regroup : in-mode regroup L₄ ≡ false
L₄-not-regroup = refl
L₄-not-guard : in-mode guard L₄ ≡ false
L₄-not-guard = refl

L₅-snap : in-mode snap L₅ ≡ true
L₅-snap = refl
L₅-regroup : in-mode regroup L₅ ≡ true
L₅-regroup = refl
L₅-not-decomp : in-mode decomp L₅ ≡ false
L₅-not-decomp = refl
L₅-not-guard : in-mode guard L₅ ≡ false
L₅-not-guard = refl

------------------------------------------------------------------------
-- 6. Guard's full star = star of 001.
--
-- The star of 001 in the Fano plane is the set of three lines
-- through e₃ = p₀₀₁, which we enumerate as {L₂, L₃, L₆}.
-- The guard's territory matches exactly.
------------------------------------------------------------------------

star-of-001 : Line → Bool
star-of-001 L₁ = false
star-of-001 L₂ = true
star-of-001 L₃ = true
star-of-001 L₄ = false
star-of-001 L₅ = false
star-of-001 L₆ = true
star-of-001 L₇ = false

guard-territory-is-star-001 :
  ∀ (ℓ : Line) → in-mode guard ℓ ≡ star-of-001 ℓ
guard-territory-is-star-001 L₁ = refl
guard-territory-is-star-001 L₂ = refl
guard-territory-is-star-001 L₃ = refl
guard-territory-is-star-001 L₄ = refl
guard-territory-is-star-001 L₅ = refl
guard-territory-is-star-001 L₆ = refl
guard-territory-is-star-001 L₇ = refl

-- The point e₃ = p₀₀₁ is on each of L₂, L₃, L₆.
001-on-L₂ : p₀₀₁ on L₂
001-on-L₂ = inj₂ (inj₁ refl)
001-on-L₃ : p₀₀₁ on L₃
001-on-L₃ = inj₂ (inj₁ refl)
001-on-L₆ : p₀₀₁ on L₆
001-on-L₆ = inj₁ refl
