------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyHom
--
-- Defines: apply-hom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyHom where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyMany



-- the arities-add ⟹ spines-compose law (the antilog/pow codec, gpowg-hom's shape):
-- applying args₁ then args₂ = applying (args₁ ++ args₂) — one antilog of the summed
-- arity. apply-many f (xs ++ ys) ≡ apply-many (apply-many f xs) ys.
apply-hom : (f : Tm) (xs ys : List Tm)
          → apply-many f (xs ++ ys) ≡ apply-many (apply-many f xs) ys
apply-hom f []       ys = refl
apply-hom f (x ∷ xs) ys = apply-hom (f ∙ x) xs ys
