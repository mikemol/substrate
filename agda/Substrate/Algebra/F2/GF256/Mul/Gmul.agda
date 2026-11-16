------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul.Gmul
--
-- Defines: gmul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul.Gmul where

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.GF256.Reduce
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



gmul : Vector 8 → Vector 8 → Vector 8
gmul a b = reduce-mod-m (a *P b)
