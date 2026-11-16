------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent.SumCong
--
-- Defines: sum-cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Idempotent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent.SumCong where

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2



sum-cong : ∀ {n m} {f g : Fin n → Vector m} → (∀ i → f i ≡ g i) → sum f ≡ sum g
sum-cong {zero}  _  = refl
sum-cong {suc _} eq = cong₂ _+ⱽ_ (eq fzero) (sum-cong (λ i → eq (fsuc i)))
