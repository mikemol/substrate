------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Defs.AntiDiagSum
--
-- Defines: anti-diag-sum
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.Defs; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec

module Substrate.Algebra.Polynomial.Graded.Defs.AntiDiagSum {A : Set} (_+_ : A → A → A) (𝟘 𝟙 : A) where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.Polynomial.Graded.Base

open Over 𝟘 using (Poly; nth)

variable n-AntiDiagSum m-AntiDiagSum k-AntiDiagSum : ℕ

open import Substrate.Algebra.Polynomial.Graded.Defs.PadEnd _+_ 𝟘 𝟙
open import Substrate.Algebra.Polynomial.Graded.Defs.PlusP _+_ 𝟘 𝟙
open import Substrate.Algebra.Polynomial.Graded.Defs.ShiftToSucOnLeft _+_ 𝟘 𝟙
open import Substrate.Algebra.Polynomial.Graded.Defs.XShift _+_ 𝟘 𝟙
anti-diag-sum : Vec (Poly m-AntiDiagSum) n-AntiDiagSum → Poly (n-AntiDiagSum ℕ+ m-AntiDiagSum)
anti-diag-sum {m-AntiDiagSum} {zero}   []           = replicate m-AntiDiagSum 𝟘
anti-diag-sum {m-AntiDiagSum} {suc n'} (row ∷ rows) =
  shift-to-suc-on-left (pad-end (suc n') row) +P x-shift (anti-diag-sum rows)

