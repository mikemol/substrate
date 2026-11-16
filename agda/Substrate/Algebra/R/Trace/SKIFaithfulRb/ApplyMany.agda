------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyMany
--
-- Defines: apply-many
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyMany where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- apply a term to a list of arguments (the n-ary spine) — the ANTILOG of the arity:
-- ONE application step, iterated arity-many times. This is `pow` of the grade-1
-- application (apply-one), the reconstruction that VARIES with arity via iteration.
apply-many : Tm → List Tm → Tm
apply-many f []       = f
apply-many f (x ∷ xs) = apply-many (f ∙ x) xs
