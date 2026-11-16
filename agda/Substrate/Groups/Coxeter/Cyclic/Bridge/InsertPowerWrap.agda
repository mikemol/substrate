------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerWrap
--
-- Defines: insert-power-wrap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ TELESCOPE RECOVERED FROM THE RETIRED PARENT @771283c8~1 (`Bridge (n : ℕ)`).
-- `Base n` is a REAL applied import here — the body reaches `insert`/`power`/`a`
-- through it — so the repair binds the argument rather than dropping the import.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Nat.Properties.Order.LtIrrefl
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Not
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Word.Length
open import Substrate.Foundation.Eq.Subst

module Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerWrap (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
open import Substrate.Groups.Coxeter.Cyclic.Base.Power



insert-power-wrap : insert a (power n) ≡ []
insert-power-wrap
  with length (power n) <? n | length-power n
... | yes p  | l≡n  = ⊥-elim (<-irrefl n (subst (λ x → x < n) l≡n p))
... | no  _  | _    = refl
