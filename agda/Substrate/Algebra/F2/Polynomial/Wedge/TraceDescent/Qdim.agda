------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.Qdim
--
-- Defines: qdim
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.Qdim where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace



-- the dimension measure on the trace carrier (degree bound: a Poly n has degree < n).
qdim : QPoly → ℕ
qdim = proj₁
