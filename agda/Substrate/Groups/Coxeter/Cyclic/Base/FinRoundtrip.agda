------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.FinRoundtrip
--
-- Defines: Fin-roundtrip
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat

module Substrate.Groups.Coxeter.Cyclic.Base.FinRoundtrip (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalToFin n
open import Substrate.Groups.Coxeter.Cyclic.Base.FinToCanonical n

Fin-roundtrip : (k : Fin (suc n)) →
  canonical-to-Fin (Fin-to-canonical k) ≡ k
Fin-roundtrip _ = refl
