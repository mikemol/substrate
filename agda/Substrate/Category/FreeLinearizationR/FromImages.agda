------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.FromImages
--
-- FLQ3 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Parametric FromImages constructor. Bundles the instance-specific
-- linear-from-images construction + universal-property witnesses
-- into a FreeLinearBuilder record; given a builder, the
-- `free-linearize-R` function lifts any image map to a
-- FreeLinearizationR record.
--
-- Each concrete LinearAlgebra instance (F₂, ℚ, ...) supplies its
-- own FreeLinearBuilder by referencing its existing
-- linear-from-images + basis-agreement + extensionality lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.FromImages where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym)

open import Substrate.Category.LinearAlgebra using (LinearAlgebra)
open import Substrate.Category.FreeLinearizationR
  using (FreeLinearizationR)

------------------------------------------------------------------------
-- 1. FreeLinearBuilder record.
--
-- Per-instance constructor data: the linear-from-images function +
-- its basis-agreement + extensionality lemmas. Each concrete
-- LinearAlgebra instance provides its own FreeLinearBuilder.
------------------------------------------------------------------------

-- ⟡set1-paydown: LinearAlgebra's R / Vector / Linear are now its params, so this
-- consumer takes them as module params; `open LinearAlgebra LA` supplies the
-- operations (apply, basis), while Vector / Linear are the params directly.
module _ (R : Set) (Vector : ℕ → Set) (Linear : ℕ → ℕ → Set) where

  record FreeLinearBuilder (LA : LinearAlgebra R Vector Linear) : Set where
    open LinearAlgebra LA
    field
      -- Construction: lift a basis-image map to a linear map.
      linear-from-images-LA :
        {n m : ℕ} → (Fin n → Vector m) → Linear n m
      -- Universal property: the lift agrees with the image map on
      -- basis vectors.
      apply-on-basis-LA :
        {n m : ℕ} (f : Fin n → Vector m) (i : Fin n) →
        apply (linear-from-images-LA f) (basis i) ≡ f i
      -- Linear-extensionality: two linear maps agreeing on basis
      -- are pointwise equal.
      linear-extensionality-LA :
        {n m : ℕ} (L₁ L₂ : Linear n m) →
        ((i : Fin n) → apply L₁ (basis i) ≡ apply L₂ (basis i)) →
        (v : Vector n) → apply L₁ v ≡ apply L₂ v

  open FreeLinearBuilder public

------------------------------------------------------------------------
-- 2. The parametric free-linearize-R constructor.
--
-- Given a LinearAlgebra LA + FreeLinearBuilder for LA + an
-- image map f : Fin n → Vector m, produce the FreeLinearizationR
-- record (canonical extension + witnesses).
------------------------------------------------------------------------

free-linearize-R :
  {R : Set} {Vector : ℕ → Set} {Linear : ℕ → ℕ → Set}
  (LA : LinearAlgebra R Vector Linear) (B : FreeLinearBuilder R Vector Linear LA) →
  {n m : ℕ} (f : Fin n → Vector m) →
  FreeLinearizationR R Vector Linear LA n m
free-linearize-R LA B f = record
  { images             = f
  ; extension          = linear-from-images-LA B f
  ; extension-on-basis = apply-on-basis-LA B f
  ; uniqueness         = λ other-ext agree-on-basis v →
      linear-extensionality-LA B
        (linear-from-images-LA B f) other-ext
        (λ i → trans (apply-on-basis-LA B f i)
                     (sym (agree-on-basis i)))
        v
  }

------------------------------------------------------------------------
-- 3. Capstone for FLQ3.
--
-- Parametric free-linearize-R defined. FLQ4 supplies the F₂
-- FreeLinearBuilder; FLQ6-FLQ7 supply ℚ's.
------------------------------------------------------------------------
