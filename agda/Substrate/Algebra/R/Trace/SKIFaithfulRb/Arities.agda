------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.Arities
--
-- Defines: arities
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.Arities where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.CF



-- the arity-grade sequence of a CF: the per-step arity (the graded cost).
arities : CF → List ℕ
arities []       = []
arities (g ∷ gs) = arity g ∷ arities gs
