------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.XP
--
-- Defines: xP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.XP where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.JacobianResidue
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Algebra.Z.MPolyNormalize
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- Non-vacuity poles (ship as terms).
------------------------------------------------------------------------

-- (a) x + x normalizes so coeff x = 2 (combine-on-equal actually fires).
xP : MPoly
xP = term (mono 1 0 0) 1ℤ ∷ term (mono 1 0 0) 1ℤ ∷ []
