------------------------------------------------------------------------
-- Substrate.Geometry.PG.Preserves
--
-- The "preserves-nonzero" predicate on F₂-linear maps. An F₂-linear
-- `L : Linear (suc n) (suc n)` acts on PG n provided it preserves
-- nonzeroness.
--
-- For invertible (GL) elements this is automatic; for general
-- linear maps it must be supplied explicitly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.PG.Preserves where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear

Preserves-Nonzero :
  ∀ {n} → Linear (suc n) (suc n) → Set
Preserves-Nonzero {n} L =
  ∀ (v : Vector (suc n)) → ¬ (v ≡ 𝟎ⱽ) → ¬ (apply L v ≡ 𝟎ⱽ)
