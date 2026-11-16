------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen
--
-- Defines: same-canonical-via-Gen
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.SameCanonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Groups.Coxeter.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.SameCanonical.Private
open import Substrate.Groups.Coxeter.SameCanonical.WordEqDec



------------------------------------------------------------------------
-- The `same-canonical` lifter.
--
-- Given decidable equality on Gen, produces `same-canonical` for any
-- Canonical predicate. The canonical witnesses are unused —
-- decidability of word equality is enough.
------------------------------------------------------------------------

same-canonical-via-Gen :
  {Gen : Set} {Canonical : Word Gen → Set} →
  ((g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)) →
  {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical-via-Gen _≟Gen_ {w₁} {w₂} _ _ = Word-≡-Dec _≟Gen_ w₁ w₂
