------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEqYes
--
-- Defines: insert-power-eq-yes
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ TELESCOPE RECOVERED FROM THE RETIRED PARENT @771283c8~1 (`Bridge (n : ℕ)`).
-- The `Dec`/`BotElim`/`Subst`/`Sym` seeds are here rather than left to
-- `unblock` because an unbound `yes`/`no` in a `with`-clause LHS surfaces as
-- `[NoParseForLHS]`, which its name-supplying loop cannot see.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Lt
-- ⚑ `Foundation.Eq` SEEDED BY HAND: `≡` is multiply-homed and `fix_notinscope`
-- picked `Category.BoundaryEvent`, which does not supply it — its own
-- read-back check caught that and reverted rather than leaving it wrong.
open import Substrate.Foundation.Eq
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

module Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEqYes (n : ℕ) where

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



------------------------------------------------------------------------
-- Bridge: insert a (power (toℕ k)) ≡ power (toℕ (σ k)).
------------------------------------------------------------------------

insert-power-eq-yes : (k : Fin (suc n)) → toℕ k < n →
                      insert a (power (toℕ k)) ≡ power (toℕ (σ k))
insert-power-eq-yes k k<n
  rewrite cyclic-suc-toℕ k
        | suc-mod-suc-lt (toℕ k) n k<n
  with length (power (toℕ k)) <? n | length-power (toℕ k)
... | yes _  | _     = refl
... | no  ¬p | l≡tk  = ⊥-elim (¬p (subst (λ x → x < n) (sym l≡tk) k<n))
