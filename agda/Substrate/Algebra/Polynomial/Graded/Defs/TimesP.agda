------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.TimesP
--
-- Defines: _*P_
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus

module Substrate.Algebra.Polynomial.Graded.Defs.TimesP {A : Set} (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-TimesP m-TimesP k-TimesP : ℕ

open import Substrate.Algebra.Polynomial.Graded.Defs.AntiDiagSum _+_ 𝟘 𝟙
open import Substrate.Algebra.Polynomial.Graded.Defs.Outer _+_ _*_ 𝟘 𝟙
infixl 7 _*P_
_*P_ : Poly n-TimesP → Poly m-TimesP → Poly (n-TimesP ℕ+ m-TimesP)
p *P q = anti-diag-sum (outer p q)

