------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.CanonicalToFin
--
-- Defines: canonical-to-Fin
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat

module Substrate.Groups.Coxeter.Cyclic.Base.CanonicalToFin (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt n

------------------------------------------------------------------------
-- 5. Bijection canonical-to-Fin / Fin-to-canonical.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w k} → Canonical-at w k → Fin (suc n)
canonical-to-Fin (c-here k) = k
