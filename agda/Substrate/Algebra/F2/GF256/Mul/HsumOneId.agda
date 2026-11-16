------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul.HsumOneId
--
-- Defines: hsum-one-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul.HsumOneId where

open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.GF256.Xtime
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Algebra.F2.GF256.Idempotent.One
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.GF256.Mul.HsumZero



hsum-one-id : (r : Vector 8) → hsum one₈ r ≡ r
hsum-one-id r = trans (cong₂ _+ⱽ_ (*ₛ-identityˡ r) (hsum-zero {7} (xtime r))) (+ⱽ-identityʳ r)
