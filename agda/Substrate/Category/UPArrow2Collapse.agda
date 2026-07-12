------------------------------------------------------------------------
-- Substrate.Category.UPArrow2Collapse
--
-- ⟡upfamily-rewire (L2 strike) — the UPArrow² → rig-cat correspondence:
-- the ι fixed-point IS the grade-index. Deletes ArrowOfArrow/UPArrow² by
-- RECOGNITION, not rebuild.
--
-- The flat `UniversalProperty.ArrowOfArrow.UPArrow²` held two UPArrows (Set₁)
-- as FIELDS plus a UPMorphism witness ⇒ `record UPArrow² : Set₂`. That is
-- `set1-is-grade-collapse` climbing the UNIVERSE tower: L0 : Set₁ → L2 : Set₂ →
-- L3 : Set₃ … one universe per meta-level. Its `commute-stated : Set` was a bare
-- stub. The tetrative tower "my favourite category is the category that is an
-- object in the category of arrow categories" was paying for the iteration in
-- UNIVERSES.
--
-- The rig cat already collapsed that tower into the ℕ-GRADE at Set₀ (Obj : ℕ →
-- Set; the ⊕/⊗ bifunctor on morphisms = OrientationBifunctor; coherence up to
-- OrientationHexagon). Here we exhibit the same collapse for the UP-arrow:
-- because `UPArrowᴳ`'s carriers are grade-indexed PARAMETERS (ℕ → Set), an arrow
-- is a Set₀ value, a family of arrows is a carrier ℕ → Set, and the arrow-OF-
-- arrows is a `UPArrowᴳ` over those families — STILL `: Set`. The tetrative LEVEL
-- became the grade; the universe did NOT climb.
--
-- `ι` (L2 → L0) is then DEFINITIONAL — the arrow-of-arrows already lives in L0's
-- universe (Set₀). The flat `ι` crossed Set₂ → Set₁ by hand; here there is no gap
-- to cross. So UPArrow²/ArrowOfArrow are redundant: recognized as the grade-index
-- of the UPArrowᴳ tower, they are deleted, and the Set₂ census slice with them.
--
-- Zero postulates, zero holes, --safe --without-K. Substrate-only.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UPArrow2Collapse where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ)

------------------------------------------------------------------------
-- An arrow, presented as a grade-indexed carrier: an arrow is a Set₀ VALUE, so a
-- family of arrows is a carrier `ℕ → Set`. This is the move UPArrow² could not
-- make (it held the arrows as FIELDS, forcing the universe up).
------------------------------------------------------------------------

Arrows : (Spec Sol : ℕ → Set) → (ℕ → Set)
Arrows Spec Sol _ = UPArrowᴳ Spec Sol

------------------------------------------------------------------------
-- THE ARROW-OF-ARROWS, as the grade-index: a UPArrowᴳ between arrow-families.
-- Measured Set₀ (was Set₂) — the universe did not climb.
------------------------------------------------------------------------

UPArrow² : (S₀ S₁ T₀ T₁ : ℕ → Set) → Set
UPArrow² S₀ S₁ T₀ T₁ = UPArrowᴳ (Arrows S₀ S₁) (Arrows T₀ T₁)

------------------------------------------------------------------------
-- ι — the fixed-point (L2 → L0): the arrow-of-arrows IS an arrow, in the SAME
-- universe (Set₀). DEFINITIONAL here — no Set₂ → Set₁ gap to cross by hand.
------------------------------------------------------------------------

ι : {S₀ S₁ T₀ T₁ : ℕ → Set} →
    UPArrow² S₀ S₁ T₀ T₁ → UPArrowᴳ (Arrows S₀ S₁) (Arrows T₀ T₁)
ι u = u

------------------------------------------------------------------------
-- THE WHOLE TETRATIVE TOWER stays at ONE universe (Set₀), indexed by the level —
-- the collapse the rig cat performs for objects/morphisms, here for UP-arrows.
-- (The flat tower was UPArrow : Set₁, UPArrow² : Set₂, UPArrow³ : Set₃, ….)
------------------------------------------------------------------------

tower : ℕ → (ℕ → Set) → (ℕ → Set) → Set
tower zero    Spec Sol = UPArrowᴳ Spec Sol
tower (suc k) Spec Sol = UPArrowᴳ (λ _ → tower k Spec Sol) (λ _ → tower k Spec Sol)
