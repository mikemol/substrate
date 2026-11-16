------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.DoubleInj
--
-- Defines: double-inj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.DoubleInj where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Double



------------------------------------------------------------------------
-- BACKWARD (~ → ≈ᵉ): the coalgebra morphism REFLECTS bisimulation too, so _≈ᵉ_ ⟺ coemit-trace-_~_ — the full
-- iff, retiring ≈ᵉ's bespoke equivalence for the pulled-back universal one. Needs code-injectivity (the
-- parity encoding is faithful): double is injective, and even (double a) ≠ odd (suc (double o)).
------------------------------------------------------------------------

double-inj : {a b : ℕ} → double a ≡ double b → a ≡ b
double-inj {zero}  {zero}  _  = refl
double-inj {suc a} {suc b} eq = cong suc (double-inj (suc-injective (suc-injective eq)))
