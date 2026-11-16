------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.UipNat
--
-- Defines: uipℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.UipNat where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- Small equational infrastructure — all one-liners by pattern on refl (no K,
-- no postulate). UIP on ℕ (Hedberg from decidable _≟_) makes the grade-equality
-- component of a morphism a MERE PROPOSITION, so it never obstructs a law.
------------------------------------------------------------------------

-- UIP on ℕ: any two grade-equalities coincide (the thin part of a morphism).
uipℕ : {i j : ℕ} (p q : i ≡ j) → p ≡ q
uipℕ = Decidable⇒UIP _≟_
