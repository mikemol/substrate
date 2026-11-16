------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.Op
--
-- Defines: σ
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat

module Substrate.Groups.Coxeter.Cyclic.Base.Op (n : ℕ) where


------------------------------------------------------------------------
-- 6. σ = cyclic-suc {n}; σ-HasOrderPerm from Slice 4.
------------------------------------------------------------------------

σ : Fin (suc n) → Fin (suc n)
σ = cyclic-suc {n}
