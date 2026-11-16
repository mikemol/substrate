------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.Outer
--
-- Defines: outer
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec

module Substrate.Algebra.Polynomial.Graded.Defs.Outer {A : Set} (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-Outer m-Outer k-Outer : ℕ

open import Substrate.Algebra.Polynomial.Graded.Defs.C _+_ _*_ 𝟘 𝟙
outer : Poly n-Outer → Poly m-Outer → Vec (Poly m-Outer) n-Outer
outer []      q = []
outer (a ∷ p) q = (a ·c q) ∷ outer p q

