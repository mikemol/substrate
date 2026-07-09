------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.MonoidalAdjunction
--
-- THE UNITING VIEW — one structure tying the fragmented graded layer together.
-- A GradedProduct satisfying the graded laws gives, AT ONCE:
--
--   * the +1-step graded WEDGE carrier   (graded-of-product : GradedDivStr),
--   * the flattened plain carrier        (flatten           : DivStr),
--   * the DEGREE as a flat GradedMonoid  (flatten-monoid    : Category.GradedMonoid),
--
-- and the graded Free⊣Forgetful adjunction (Graded.Adjunction) applies to its
-- graded carrier, while the morphism connectors (Graded.Morphism) carry between
-- all three. So "graded monoidal adjunction over the wedge carrier" is one
-- object with five faces (carrier / morphism / adjunction / UP / degree),
-- assembled from existing parts — only the bundling is new.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.MonoidalAdjunction where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Algebra.Wedge using (DivStr)
-- ⟡set1-paydown: GradedDivStr AND GradedProduct now carry their graded carrier as a
-- module param (no `C` projection). GradedMonoidalAdjunction is thus parameterized
-- over that carrier family C : ℕ → Set (its `prod` is a `GradedProduct C`); it drops
-- Set₁ → Set. Consumers write `GradedMonoidalAdjunction C`.
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; graded-of-product; flatten)
open import Substrate.Algebra.Wedge.Product.LawTypes
  using (GradedAssoc; GradedUnitˡ; GradedUnitʳ)
open import Substrate.Algebra.Wedge.Graded.Adjunction using (gTerm)

------------------------------------------------------------------------
-- 1. The uniting record: a GradedProduct + its graded laws.
------------------------------------------------------------------------

module _ (C : ℕ → Set) where

  record GradedMonoidalAdjunction : Set where
    field
      prod  : GradedProduct C
      assoc : GradedAssoc prod
      unitˡ : GradedUnitˡ prod
      unitʳ : GradedUnitʳ prod

  open GradedMonoidalAdjunction public

------------------------------------------------------------------------
-- 2. The carriers (proof-free faces), all from the one structure. The DEGREE
--    (which uses the flatten construction) and the Vec instance — being
--    proof-dependent (Product.Laws) — live in
--    Substrate.Algebra.Wedge.Graded.MonoidalAdjunction.Properties, per the
--    def/proof separation policy.  (C inferred from the gma argument.)
------------------------------------------------------------------------

graded-carrier : {C : ℕ → Set} (gma : GradedMonoidalAdjunction C) →
                 GradedDivStr C (λ _ → C 1)
graded-carrier gma = graded-of-product (prod gma)

flat-carrier : {C : ℕ → Set} → GradedMonoidalAdjunction C → DivStr
flat-carrier gma = flatten (prod gma)

-- the graded Free⊣Forgetful hom-set (Graded.Adjunction) over this carrier.
gma-term : {C : ℕ → Set} (gma : GradedMonoidalAdjunction C) (n : ℕ) →
           C (suc n) → C n → Set
gma-term gma = gTerm (graded-carrier gma)
