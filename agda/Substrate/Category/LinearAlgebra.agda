------------------------------------------------------------------------
-- Substrate.Category.LinearAlgebra
--
-- FLQ1 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Abstract record bundling the ambient structure of a "linear
-- algebra over R": scalar carrier R, dimension-indexed Vector
-- family, dimension-indexed Linear-map family, basis vectors, and
-- the four basic operations (+R, +V, *R-scalar, apply).
--
-- Concrete instances (F₂ at FLQ4, ℚ at FLQ6) populate this
-- record with their specific Vector / Linear / basis. FLQ2
-- builds FreeLinearizationR over arbitrary LinearAlgebra
-- instances.
--
-- Per [[feedback-categorical-name-first]]: "category of finite-
-- dimensional R-modules with a chosen basis" is the standard
-- categorical name; LinearAlgebra is its bundled data form.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.LinearAlgebra where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)

------------------------------------------------------------------------
-- 1. The LinearAlgebra record.
--
-- Bundles (R, Vector R, Linear R, basis, apply) + the basic
-- operations. Per-instance LAWS are NOT fields here — each
-- concrete instance proves its own laws separately; the record
-- just supplies the OPERATIONS.
------------------------------------------------------------------------

-- ⟡set1-paydown: the scalar carrier R : Set, the dimension-indexed vector family
-- Vector : ℕ → Set, and the linear-map family Linear : ℕ → ℕ → Set are all
-- Set-VALUED, so — per the substrate stance (carriers/families are module params,
-- never fields) — all three become module parameters; only the operations stay
-- fields. LinearAlgebra drops Set₁ → Set; consumers write `LinearAlgebra R Vector
-- Linear`, and the old `R L` / `Vector L` / `Linear L` projections become the params.
module _ (R : Set) (Vector : ℕ → Set) (Linear : ℕ → ℕ → Set) where

  record LinearAlgebra : Set where
    field
      -- Field elements
      zeroR : R
      oneR  : R
      -- Vector operations
      zeroV : {n : ℕ} → Vector n
      _+V_  : {n : ℕ} → Vector n → Vector n → Vector n
      _*S_  : {n : ℕ} → R → Vector n → Vector n
      -- Basis vectors
      basis : {n : ℕ} → Fin n → Vector n
      -- Linear-map application
      apply : {n m : ℕ} → Linear n m → Vector n → Vector m

  open LinearAlgebra public

------------------------------------------------------------------------
-- 2. Capstone for FLQ1.
--
-- LinearAlgebra abstract record defined. FLQ2 builds the
-- FreeLinearizationR primitive parametric in a LinearAlgebra
-- instance; FLQ4 + FLQ6 supply F₂ and ℚ instances.
------------------------------------------------------------------------
