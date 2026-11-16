------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.PadEnd
--
-- Defines: pad-end
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec

module Substrate.Algebra.Polynomial.Graded.Defs.PadEnd {A : Set} (_+_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-PadEnd m-PadEnd k-PadEnd : ℕ

pad-end : (k-PadEnd : ℕ) → Poly n-PadEnd → Poly (n-PadEnd ℕ+ k-PadEnd)
pad-end k-PadEnd []      = replicate k-PadEnd 𝟘
pad-end k-PadEnd (x ∷ p) = x ∷ pad-end k-PadEnd p

