------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx
--
-- Defines: inv-inv-canonical-ex
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.CongTrans
module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Existential n
-- ⚑ `Cyclic.Inverse` DISSOLVED (771283c8) — this file uses THREE of its leaves
-- (`inv`, `inv-power-eq`, `inv-pos`), each now named (Ⓐ¹²′).
-- ⚑ `…InvInv.Private` DROPPED: `--provides` reports ZERO names.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosInvPos n



------------------------------------------------------------------------
-- 2. inv-inv-canonical-ex: the generic double-inverse property.
------------------------------------------------------------------------

inv-inv-canonical-ex : ∀ {w} → Canonical-ex w → inv (inv w) ≡ w
inv-inv-canonical-ex = canonical-cover-ex
  (λ {w} _ → inv (inv w) ≡ w)
  per-pos
  where
    per-pos : (k : Fin (suc n)) →
              inv (inv (power (toℕ k))) ≡ power (toℕ k)
    per-pos k =
      cong-trans inv (inv-power-eq k)
      (trans (inv-power-eq (inv-pos k))
             (cong power (toℕ-inv-pos-inv-pos k)))
