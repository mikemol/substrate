------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.EqMSound
--
-- Defines: eqM-sound
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.EqMSound where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.EqNatSound



eqM-sound : {m n : Mono} → eqM m n ≡ tt → m ≡ n
eqM-sound {mono a b c} {mono d e f} h =
  cong₃ mono (eqℕ-sound (and-l {eqℕ a d} h))
             (eqℕ-sound (and-l {eqℕ b e} (and-r {eqℕ a d} h)))
             (eqℕ-sound (and-r {eqℕ b e} (and-r {eqℕ a d} h)))
