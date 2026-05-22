------------------------------------------------------------------------
-- Substrate.Geometry.PG.Projections
--
-- The two projections from a PG point:
--   PG-coords  → underlying F₂-vector
--   PG-nonzero → witness that the vector is non-zero
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.PG.Projections where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.F2.Vector
open import Substrate.Geometry.PG.Type using (PG)

PG-coords : ∀ {n} → PG n → Vector (suc n)
PG-coords = proj₁

PG-nonzero : ∀ {n} (p : PG n) → ¬ (PG-coords p ≡ 𝟎ⱽ)
PG-nonzero = proj₂
