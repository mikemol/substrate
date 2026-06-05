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
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr; C)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; graded-of-product; flatten)
open import Substrate.Algebra.Wedge.Product.LawTypes
  using (GradedAssoc; GradedUnitˡ; GradedUnitʳ)
open import Substrate.Algebra.Wedge.Graded.Adjunction using (gTerm)

------------------------------------------------------------------------
-- 1. The uniting record: a GradedProduct + its graded laws.
------------------------------------------------------------------------

record GradedMonoidalAdjunction : Set₁ where
  field
    prod  : GradedProduct
    assoc : GradedAssoc prod
    unitˡ : GradedUnitˡ prod
    unitʳ : GradedUnitʳ prod

open GradedMonoidalAdjunction public

------------------------------------------------------------------------
-- 2. The carriers (proof-free faces), all from the one structure. The DEGREE
--    (which uses the flatten construction) and the Vec instance — being
--    proof-dependent (Product.Laws) — live in
--    Substrate.Algebra.Wedge.Graded.MonoidalAdjunction.Properties, per the
--    def/proof separation policy.
------------------------------------------------------------------------

graded-carrier : GradedMonoidalAdjunction → GradedDivStr
graded-carrier gma = graded-of-product (prod gma)

flat-carrier : GradedMonoidalAdjunction → DivStr
flat-carrier gma = flatten (prod gma)

-- the graded Free⊣Forgetful hom-set (Graded.Adjunction) over this carrier.
gma-term : (gma : GradedMonoidalAdjunction) (n : ℕ) →
           C (graded-carrier gma) (suc n) → C (graded-carrier gma) n → Set
gma-term gma = gTerm (graded-carrier gma)
