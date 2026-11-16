------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.CanonicalCover
--
-- Defines: canonical-cover
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

module Substrate.Groups.Coxeter.Cyclic.Base.CanonicalCover (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt n

------------------------------------------------------------------------
-- 4. canonical-cover — Fin-indexed dispatch.
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w k} → Canonical-at w k → Set ℓ) →
  ((k : Fin (suc n)) → P (c-here k)) →
  ∀ {w k} (c : Canonical-at w k) → P c
canonical-cover P f (c-here k) = f k
