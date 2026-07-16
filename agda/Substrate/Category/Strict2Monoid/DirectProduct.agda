------------------------------------------------------------------------
-- Substrate.Category.Strict2Monoid.DirectProduct
--
-- The direct product of two Strict2Monoids is a Strict2Monoid.
--
-- This generalizes substrate's Coxeter.DirectProduct (which works at
-- the Coxeter-Core level) to the categorical Strict2Monoid level.
-- Any two Strict2Monoids compose via componentwise operations on
-- pairs.
--
-- This module IS the interchange-law-for-DirectProduct content
-- promised by the arc's slice 8: the two underlying composition axes
-- (one per component) commute componentwise, which is exactly the
-- "axes don't interfere" property of direct products. The 2-cell
-- structure (≈) lifts via product-of-equalities.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Strict2Monoid.DirectProduct where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; cong₂)

open import Substrate.Category.Strict2Monoid

private
  variable
    ℓ₁ ℓ₂ ℓ₁′ ℓ₂′ : Level

------------------------------------------------------------------------
-- N-1: DirectProduct of two Strict2Monoids.
------------------------------------------------------------------------

-- ⟡set1-rp-strict2monoid: the carriers/relations are record PARAMS now — bind them as implicit
-- indices (A₁/_≈₁_/A₂/_≈₂_) and carry the product carrier + componentwise relation IN THE TYPE
-- (the ex-fields `M`/`_≈_` of the result). The ex-projections `M₁.M`/`M₁._≈_` ARE those indices.
direct-product :
  {A₁ : Set ℓ₁} {_≈₁_ : A₁ → A₁ → Set ℓ₁′}
  {A₂ : Set ℓ₂} {_≈₂_ : A₂ → A₂ → Set ℓ₂′} →
  Strict2Monoid ℓ₁ ℓ₁′ A₁ _≈₁_ →
  Strict2Monoid ℓ₂ ℓ₂′ A₂ _≈₂_ →
  Strict2Monoid (ℓ₁ ⊔ ℓ₂) (ℓ₁′ ⊔ ℓ₂′) (A₁ × A₂)
                (λ (a₁ , a₂) (b₁ , b₂) → (a₁ ≈₁ b₁) × (a₂ ≈₂ b₂))
direct-product M₁ M₂ = record
  { _·_         = λ (a₁ , a₂) (b₁ , b₂) → (a₁ M₁.· b₁ , a₂ M₂.· b₂)
  ; ε           = (M₁.ε , M₂.ε)
  ; ·-assoc     = λ (a₁ , a₂) (b₁ , b₂) (c₁ , c₂) →
                    cong₂ _,_ (M₁.·-assoc a₁ b₁ c₁) (M₂.·-assoc a₂ b₂ c₂)
  ; ·-identityˡ = λ (a₁ , a₂) →
                    cong₂ _,_ (M₁.·-identityˡ a₁) (M₂.·-identityˡ a₂)
  ; ·-identityʳ = λ (a₁ , a₂) →
                    cong₂ _,_ (M₁.·-identityʳ a₁) (M₂.·-identityʳ a₂)
  ; ≈-refl      = (M₁.≈-refl , M₂.≈-refl)
  ; ≈-sym       = λ (p₁ , p₂) → (M₁.≈-sym p₁ , M₂.≈-sym p₂)
  ; ≈-trans     = λ (p₁ , p₂) (q₁ , q₂) →
                    (M₁.≈-trans p₁ q₁ , M₂.≈-trans p₂ q₂)
  ; ·-cong      = λ (p₁ , p₂) (q₁ , q₂) →
                    (M₁.·-cong p₁ q₁ , M₂.·-cong p₂ q₂)
  }
  where
    module M₁ = Strict2Monoid M₁
    module M₂ = Strict2Monoid M₂

------------------------------------------------------------------------
-- N-2: Capstone — Strict2Monoid is closed under direct product.
--
-- The combinator iterates: nested direct-product gives strict 3-, 4-,
-- ..., n-monoids. Each layer adds one composition axis, all commuting
-- via componentwise operations.
--
-- The "interchange law" between the two axes in a DirectProduct is
-- DEFINITIONAL — componentwise operations on disjoint components
-- can't interfere. The 2-cell structure (≈) propagates similarly.
--
-- Per [[project-graded-bicategorical-arc]]: this combinator opens
-- the substrate's higher-categorical infrastructure. Any tower of
-- DirectProducts gives a strict n-monoid; the substrate's existing
-- Coxeter.DirectProduct is the Coxeter-flavored specialization.
--
-- Deferred follow-ons:
--
--   * **GradedMonoid.DirectProduct**: same combinator for GradedMonoid
--     records (degrees add componentwise).
--
--   * **Lift Z₃ × FreeCyclic to direct-product Strict2Monoid**:
--     instead of building Z₃-x-FreeCyclic via Coxeter.DirectProduct,
--     build it via direct-product on Strict2Monoid instances.
--     Equivalent structure; different abstraction layer.
------------------------------------------------------------------------
