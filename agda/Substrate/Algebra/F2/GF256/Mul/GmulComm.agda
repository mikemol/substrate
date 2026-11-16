------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul.GmulComm
--
-- Defines: gmul-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul.GmulComm where

open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.RingLaws.Comm
open import Substrate.Algebra.F2.GF256.Reduce
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.GF256.Mul.Gmul



gmul-comm : (a b : Vector 8) → gmul a b ≡ gmul b a
gmul-comm a b = trans (cong reduce-mod-m (*P-comm a b)) (reduce-subst (+ℕ-comm 8 8) (b *P a))
