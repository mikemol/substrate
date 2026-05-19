------------------------------------------------------------------------
-- Substrate.Category.RGradedMonoid
--
-- R-graded monoid for any commutative monoid R. Generalizes
-- Substrate.Category.GradedMonoid (which fixes R = ℕ) to arbitrary
-- commutative monoid gradings.
--
-- For R = ℕ: recovers the standard ℕ-graded monoid.
-- For R = F₂ (Z/2): parity-graded structures — V₄'s 3+1 split, etc.
-- For R = Z/p: p-grading at any prime.
--
-- Per [[project-3plus1-as-graded-cocycle]]: F₂-graded structures
-- give the substrate's natural reading of the 3+1 parity universal
-- as a degree-1 cocycle in Z/2-grading.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RGradedMonoid where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Category.CommutativeMonoid

private
  variable
    ℓ ℓR : Level

------------------------------------------------------------------------
-- The R-graded GradedMonoid record.
--
-- Parameterized by a CommutativeMonoid R (the grading group).
-- The underlying monoid M has a degree function M → R that's a
-- monoid homomorphism into R.
------------------------------------------------------------------------

record RGradedMonoid (𝓡 : CommutativeMonoid ℓR) (ℓ : Level) : Set (ℓR ⊔ lsuc ℓ) where
  open CommutativeMonoid 𝓡
  field
    -- Underlying monoid.
    M : Set ℓ
    _·_ : M → M → M
    ε : M
    -- Monoid laws.
    ·-assoc      : (a b c : M) → (a · b) · c ≡ a · (b · c)
    ·-identityˡ  : (a : M) → ε · a ≡ a
    ·-identityʳ  : (a : M) → a · ε ≡ a
    -- Degree function valued in R.
    degree       : M → R
    degree-ε     : degree ε ≡ 0R
    degree-·     : (a b : M) → degree (a · b) ≡ degree a +R degree b

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: ANY CommutativeMonoid R can serve as the grading
-- for a graded monoid. ℕ-graded (slice 4) is the R = ℕ instance;
-- F₂-graded (subsequent slices) is the R = F₂ instance, with
-- substrate-wide parity grading consequences.
--
-- The R-graded structure is naturally categorical: a monoid M with
-- an R-valued degree IS a monoid homomorphism M → R, where R is
-- itself a commutative monoid. The record packages this.
------------------------------------------------------------------------
