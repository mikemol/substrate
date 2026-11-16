------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.PlusP
--
-- Defines: _+P_
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec

module Substrate.Algebra.Polynomial.Graded.Defs.PlusP {A : Set} (_+_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-PlusP m-PlusP k-PlusP : ℕ

infixl 6 _+P_
_+P_ : Poly n-PlusP → Poly n-PlusP → Poly n-PlusP
[]      +P []      = []
(x ∷ u) +P (y ∷ v) = (x + y) ∷ (u +P v)

