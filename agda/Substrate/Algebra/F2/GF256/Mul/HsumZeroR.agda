------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul.HsumZeroR
--
-- Defines: hsum-zeroʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul.HsumZeroR where

open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.GF256.Reduce
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



hsum-zeroʳ : ∀ {n} (p : Polynomial n) → hsum p 𝟎ⱽ ≡ 𝟎ⱽ
hsum-zeroʳ []      = refl
hsum-zeroʳ (a ∷ p) =
  trans (cong₂ _+ⱽ_ (*ₛ-zeroʳ a) (trans (cong (hsum p) xtime-zero) (hsum-zeroʳ p))) (+ⱽ-identityˡ 𝟎ⱽ)
