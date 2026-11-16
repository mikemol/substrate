------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.ShiftToSucOnLeft
--
-- Defines: shift-to-suc-on-left
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm

module Substrate.Algebra.Polynomial.Graded.Defs.ShiftToSucOnLeft {A : Set} (_+_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-ShiftToSucOnLeft m-ShiftToSucOnLeft k-ShiftToSucOnLeft : ℕ

shift-to-suc-on-left : ∀ {n'} → Poly (m-ShiftToSucOnLeft ℕ+ suc n') → Poly (suc n' ℕ+ m-ShiftToSucOnLeft)
shift-to-suc-on-left {m-ShiftToSucOnLeft} {n'} p = subst Poly (+ℕ-comm m-ShiftToSucOnLeft (suc n')) p

