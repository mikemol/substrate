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

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Not

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Foundation.Eq

Preserves-Nonzero :
  ∀ {n} → Linear (suc n) (suc n) → Set
Preserves-Nonzero {n} L =
  ∀ (v : Vector (suc n)) → ¬ (v ≡ 𝟎ⱽ) → ¬ (apply L v ≡ 𝟎ⱽ)
