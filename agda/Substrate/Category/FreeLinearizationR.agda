------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR
--
-- FLQ2 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Parametric "free-linearisation over R" primitive. Generalises
-- Substrate.Category.FreeLinearization from F₂ to any
-- LinearAlgebra instance (FLQ1).
--
-- Universal property: any function `Fin n → Vector m` extends
-- uniquely to a Linear n m. The record bundles the data + the
-- two witnesses (extension-on-basis, uniqueness).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.LinearAlgebra using (LinearAlgebra)

------------------------------------------------------------------------
-- 1. The FreeLinearizationR record.
--
-- Parametric in a LinearAlgebra instance LA. The record's fields
-- reference LA's Vector and Linear families.
------------------------------------------------------------------------

-- ⟡set1-paydown: LinearAlgebra's R / Vector / Linear are now its params, so this
-- consumer takes them as module params; `open LinearAlgebra LA` still supplies the
-- operations (apply, basis, …), while Vector / Linear are the params directly.
module _ (R : Set) (Vector : ℕ → Set) (Linear : ℕ → ℕ → Set) where

  record FreeLinearizationR (LA : LinearAlgebra R Vector Linear) (n m : ℕ) : Set where
    open LinearAlgebra LA
    field
      images :
        Fin n → Vector m
      extension :
        Linear n m
      extension-on-basis :
        (i : Fin n) → apply extension (basis i) ≡ images i
      uniqueness :
        (other : Linear n m) →
        ((i : Fin n) → apply other (basis i) ≡ images i) →
        (v : Vector n) → apply extension v ≡ apply other v

  open FreeLinearizationR public

------------------------------------------------------------------------
-- 2. Capstone for FLQ2.
--
-- Parametric FreeLinearizationR defined. FLQ3 adds the
-- FromImages constructor; FLQ4-FLQ7 supply F₂ and ℚ instances.
------------------------------------------------------------------------
