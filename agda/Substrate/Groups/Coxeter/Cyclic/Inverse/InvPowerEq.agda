------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq
--
-- Defines: inv-power-eq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Inverse; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Groups.Coxeter.Word.Length
module Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
-- ⚑ `…Cyclic.Bridge n` DROPPED (Ⓑ2c-BRIDGE10″) — a pure CONDUIT here: every name
-- the body uses came through Bridge's `open import …Base n public`, and `Base` is
-- imported directly above.  ⚑ Siblings APPLIED, post-telescope-repair.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtPowerToNat n



-- inv on `power (toℕ k)` reduces to `power (toℕ (inv-pos k))`. Exposed
-- so downstream proofs (InvCanonical.{Left, Right, InvInv}) can use it
-- without re-deriving the length-check + fromℕ<-roundtrip dance.
inv-power-eq : (k : Fin (suc n)) →
               inv (power (toℕ k)) ≡ power (toℕ (inv-pos k))
inv-power-eq k with length (power (toℕ k)) <? suc n | length-power (toℕ k)
... | yes p | _    = cong (λ x → power (toℕ (inv-pos x))) (fromℕ<-power-toℕ k p)
... | no ¬p | l≡tk = ⊥-elim (¬p (subst (λ x → x < suc n) (sym l≡tk) (toℕ-bound k)))
