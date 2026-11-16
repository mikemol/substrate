------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.RebuildK
--
-- Defines: rebuild-K
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.RebuildK where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.FaithfulRb
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- and each generator faithfully rebuilds its redex (K∙x∙y, I∙x) — the antilog at arity:
rebuild-K : faithful-rb gK (K ∷ I ∷ []) ≡ ((K ∙ K) ∙ I)
rebuild-K = refl
