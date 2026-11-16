------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.HasOrderPerm
--
-- Defines: σ-HasOrderPerm
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Foundation.Nat.Nat

module Substrate.Groups.Coxeter.Cyclic.Base.HasOrderPerm (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.Op n

σ-HasOrderPerm : HasOrderPerm σ (suc n)
σ-HasOrderPerm = cyclic-suc-HasOrderPerm {n}
