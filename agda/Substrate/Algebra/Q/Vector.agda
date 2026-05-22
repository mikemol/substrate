------------------------------------------------------------------------
-- Substrate.Algebra.Q.Vector
--
-- Q8 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- ℚ-vectors of fixed length n via stdlib Data.Vec. Sister
-- structure to Substrate.Algebra.F2.Vector — same shape, ℚ
-- entries instead of F₂ entries.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Vector where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate; lookup; zipWith; map)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; cong₂)

open import Substrate.Algebra.Q
  using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Arithmetic
  using (_+ℚ_; _*ℚ_; -ℚ_)

------------------------------------------------------------------------
-- 1. Vector type and zero.
------------------------------------------------------------------------

Vector : ℕ → Set
Vector n = Vec ℚ n

𝟎ℚⱽ : ∀ {n} → Vector n
𝟎ℚⱽ {n} = replicate n 0ℚ

------------------------------------------------------------------------
-- 2. Componentwise addition.
------------------------------------------------------------------------

infixl 6 _+ℚⱽ_

_+ℚⱽ_ : ∀ {n} → Vector n → Vector n → Vector n
_+ℚⱽ_ = zipWith _+ℚ_

------------------------------------------------------------------------
-- 3. Scalar multiplication.
------------------------------------------------------------------------

infixl 7 _*ℚₛ_

_*ℚₛ_ : ∀ {n} → ℚ → Vector n → Vector n
c *ℚₛ v = map (c *ℚ_) v

------------------------------------------------------------------------
-- 4. Negation.
------------------------------------------------------------------------

-ℚⱽ_ : ∀ {n} → Vector n → Vector n
-ℚⱽ_ = map -ℚ_

------------------------------------------------------------------------
-- 5. Basis vectors.
--
-- e_i has 1ℚ at position i, 0ℚ elsewhere.
------------------------------------------------------------------------

basis-ℚ : ∀ {n} → Fin n → Vector n
basis-ℚ {suc _} zero    = 1ℚ ∷ 𝟎ℚⱽ
basis-ℚ {suc _} (suc i) = 0ℚ ∷ basis-ℚ i

------------------------------------------------------------------------
-- 6. Capstone for Q8.
--
-- ℚ-Vector with componentwise +, scalar *, negation, basis
-- vectors. Q9 builds ℚ-linear maps.
------------------------------------------------------------------------
