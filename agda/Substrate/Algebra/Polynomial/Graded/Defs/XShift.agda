------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.XShift
--
-- Defines: x-shift
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec

module Substrate.Algebra.Polynomial.Graded.Defs.XShift {A : Set} (_+_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-XShift m-XShift k-XShift : ℕ

x-shift : Poly n-XShift → Poly (suc n-XShift)
x-shift p = 𝟘 ∷ p

