------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerAdvance
--
-- Defines: insert-power-advance
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ TELESCOPE RECOVERED FROM THE RETIRED PARENT @771283c8~1 (`Bridge (n : ℕ)`).
-- The decomposition dropped the parameter and kept the applied `Base n`.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Word.Length
open import Substrate.Foundation.Nat.Lt2
-- ⚑ `yes`/`no` SURFACE AS `[NoParseForLHS]`, NOT `[NotInScope]` — an unbound
-- constructor in a `with`-clause LHS is a PARSE failure, so `unblock`'s
-- name-supplying loop cannot see it and correctly refuses rather than guessing.
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym

module Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerAdvance (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
open import Substrate.Groups.Coxeter.Cyclic.Base.Power



------------------------------------------------------------------------
-- Per-case insert helpers (used by Core for power-canonical-bounded
-- and insert-append-lemma).
------------------------------------------------------------------------

insert-power-advance : (k : ℕ) → k < n → insert a (power k) ≡ a ∷ power k
insert-power-advance k k<n
  with length (power k) <? n | length-power k
... | yes _  | _    = refl
... | no  ¬p | l≡k  = ⊥-elim (¬p (subst (λ x → x < n) (sym l≡k) k<n))
