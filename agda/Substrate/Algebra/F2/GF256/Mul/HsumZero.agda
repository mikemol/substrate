------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul.HsumZero
--
-- Defines: hsum-zero
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul.HsumZero where

open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.GF256.Xtime
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2



hsum-zero : ∀ {n} (r : Vector 8) → hsum (𝟎ⱽ {n}) r ≡ 𝟎ⱽ
hsum-zero {zero}  r = refl
hsum-zero {suc n} r = trans (cong₂ _+ⱽ_ (*ₛ-absorbˡ r) (hsum-zero {n} (xtime r))) (+ⱽ-identityˡ 𝟎ⱽ)
