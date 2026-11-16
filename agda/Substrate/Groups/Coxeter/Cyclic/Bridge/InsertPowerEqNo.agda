------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEqNo
--
-- Defines: insert-power-eq-no
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ TELESCOPE RECOVERED FROM THE RETIRED PARENT @771283c8~1 (`Bridge (n : ℕ)`).
-- Seeds: `Dec` (an unbound `yes`/`no` in a `with`-LHS reads as `[NoParseForLHS]`,
-- invisible to `unblock`) and `Eq` (`≡` is multiply-homed, and the index's first
-- pick does not supply it).
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Lt
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Groups.Coxeter.Word.Length
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Properties.Order

module Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEqNo (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
-- ⚑ APPLIED, because `NotLtEqN` regained the parent's `(n : ℕ)` telescope in
-- this same pass.  Unapplied it elaborates at a FRESH metavariable and the
-- mismatch surfaces as `[UnequalTerms]`, not as a scope error — which is why
-- `unblock` supplied nine names and then correctly stopped.
open import Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtEqN n


insert-power-eq-no : (k : Fin (suc n)) → ¬ (toℕ k < n) →
                     insert a (power (toℕ k)) ≡ power (toℕ (σ k))
insert-power-eq-no k ¬k<n
  rewrite cyclic-suc-toℕ k
        | not-lt-eq-n k ¬k<n
        | suc-mod-suc-self n
  with length (power n) <? n | length-power n
... | yes p  | l≡n  = ⊥-elim (<-irrefl n (subst (λ x → x < n) l≡n p))
... | no  _  | _    = refl
