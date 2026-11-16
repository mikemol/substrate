------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.CanonicalBezout.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.CanonicalBezout; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.CanonicalBezout.Private where

open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst



open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Z.Int
open import Substrate.Foundation.Eq
-- The Bézout route agrees on the same closed witness (2/4 ≈ 1/2).
