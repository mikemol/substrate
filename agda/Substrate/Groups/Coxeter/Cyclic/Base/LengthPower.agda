------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
--
-- Defines: length-power
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
open import Substrate.Groups.Coxeter.Word.Length

module Substrate.Groups.Coxeter.Cyclic.Base.LengthPower where

open import Substrate.Groups.Coxeter.Cyclic.Base.Power

length-power : (k : ℕ) → length (power k) ≡ k
length-power zero    = refl
length-power (suc k) = cong suc (length-power k)
