------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent.HsumIsSum
--
-- Defines: hsum-is-sum
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Idempotent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent.HsumIsSum where

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.GF256.Xtime
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.GF256.Idempotent.Xpow



-- hsum is the basis-weighted sum (the fold = Σᵢ pᵢ ·ₛ xtimeⁱ r).
hsum-is-sum : ∀ {n} (p : Polynomial n) (r : Vector 8)
            → hsum p r ≡ sum (λ i → lookup p i *ₛ xpow (toℕ i) r)
hsum-is-sum []      r = refl
hsum-is-sum (a ∷ p) r = cong (λ z → (a *ₛ r) +ⱽ z) (hsum-is-sum p (xtime r))
