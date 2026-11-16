------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
--
-- Defines: Canonical-at
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat
open import Substrate.Groups.Coxeter.Word

module Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.Power

------------------------------------------------------------------------
-- 3. Canonical-at w k — length-indexed.
------------------------------------------------------------------------

data Canonical-at : Word Gen → Fin (suc n) → Set where      -- ⟦shape:421aa4ad c-here⟧
  c-here : (k : Fin (suc n)) → Canonical-at (power (toℕ k)) k
