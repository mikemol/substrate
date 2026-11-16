------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.FinToCanonical
--
-- Defines: Fin-to-canonical
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat

module Substrate.Groups.Coxeter.Cyclic.Base.FinToCanonical (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power

Fin-to-canonical : (k : Fin (suc n)) → Canonical-at (power (toℕ k)) k
Fin-to-canonical k = c-here k
