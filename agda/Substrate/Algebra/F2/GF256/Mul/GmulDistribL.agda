------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul.GmulDistribL
--
-- Defines: gmul-distribˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul.GmulDistribL where

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.RingLaws.Distrib
open import Substrate.Algebra.F2.GF256.Reduce
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.GF256.Mul.Gmul



gmul-distribˡ : (a b c : Vector 8) → gmul a (b +ⱽ c) ≡ gmul a b +ⱽ gmul a c
gmul-distribˡ a b c = trans (cong reduce-mod-m (*P-distribˡ a b c)) (reduce-+ⱽ (a *P b) (a *P c))
