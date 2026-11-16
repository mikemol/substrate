------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.Power
--
-- Defines: power
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
open import Substrate.Groups.Coxeter.Word

module Substrate.Groups.Coxeter.Cyclic.Base.Power where

open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

------------------------------------------------------------------------
-- 2. power k = aᵏ as a Word.
------------------------------------------------------------------------

power : ℕ → Word Gen
power zero    = []
power (suc k) = a ∷ power k
