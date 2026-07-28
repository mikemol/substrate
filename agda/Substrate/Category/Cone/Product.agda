------------------------------------------------------------------------
-- Substrate.Category.Cone.Product
--
-- The categorical product as a Cone over a discrete (no morphisms
-- between objects) base diagram.
--
-- Given a finite family of types Base : Fin n → Set, the product
-- (Σ-style or Π-style) is the apex of the universal cone over Base.
-- This module presents the trivial / canonical Cone where the apex
-- is the dependent function space `(i : Fin n) → Base i` and the
-- legs are evaluation at each index.
--
-- Substrate connection: this is the simplest non-trivial Cone
-- instance. Any (3, 1)-cone, (4, 1)-cone, etc. with a discrete base
-- recovers via this primitive when the apex is the product.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.Product where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.Cone

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- N-1: The dependent-product apex.
--
-- For a finite Base : Fin n → Set, the apex `(i : Fin n) → Base i`
-- IS the categorical product. Each "leg" is just function evaluation
-- at the given index.
------------------------------------------------------------------------

product-apex : ∀ {n} (Base : Fin n → Set ℓ) → Set ℓ
product-apex {n = n} Base = (i : Fin n) → Base i

------------------------------------------------------------------------
-- N-2: The product as a Cone.
--
-- Legs are evaluation. This is the substrate's canonical "product
-- cone" — the cone whose apex is the universal product of the base.
------------------------------------------------------------------------

product-cone : ∀ {n} (Base : Fin n → Set ℓ) →
               Cone n Base (product-apex Base)
product-cone Base = record
  { leg = λ i x → x i
  }

------------------------------------------------------------------------
-- N-3: Capstone.
--
-- After this slice: any discrete-base cone has a canonical "product"
-- realization where the apex is the dependent function space and
-- legs are evaluations.
--
-- For substrate's M:N cone instances: when the base is discrete
-- (M readings with no structural morphisms between them), the
-- product-cone realization gives the universal apex.
--
-- Non-discrete bases (with morphisms between base objects, e.g.,
-- Equalizer's parallel pair or Pullback's cospan) need richer cones
-- where the leg satisfies commutativity conditions with base
-- morphisms — deferred.
------------------------------------------------------------------------
