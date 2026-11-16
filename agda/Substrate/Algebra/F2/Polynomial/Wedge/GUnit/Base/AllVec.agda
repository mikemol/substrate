------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVec
--
-- Defines: all-vec
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVec where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Bool
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — a RETIRED barrel and a banned
-- `as` alias in one statement, the shape all 26 surviving references to that
-- barrel share.  The three qualified names (`F2.F₂`, `F2.𝟘`, `F2.𝟙`) all come
-- from ONE leaf, so the alias bought nothing the bare import does not.
open import Substrate.Algebra.F2.F2



-- generic exhaustion over all 2^n bit-vectors + soundness.
all-vec : {n : ℕ} (P : Vec F₂ n → Bool) → Bool
all-vec {zero}  P = P []
all-vec {suc n} P = all-vec (λ v → P (𝟘 ∷ v)) ∧ all-vec (λ v → P (𝟙 ∷ v))
