------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPos
--
-- Defines: toℕ-inv-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPos (n : ℕ) where

-- ⚑ `Cyclic.Inverse` DISSOLVED (771283c8) — `inv-pos` is `Inverse.InvPos`'s (Ⓐ¹²′).
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
-- ⚑ `…InvInv.Private` DROPPED: `--provides` reports it defines ZERO names.  The
-- split emitted an empty module — header, one import, a section comment — and
-- four siblings still import it.  Importing nothing is not an error, which is
-- why it survived; it is dead weight the decomposition left behind.


toℕ-inv-pos : (k : Fin (suc n)) →
              toℕ (inv-pos k) ≡ (suc n ∸ toℕ k) mod-suc n
toℕ-inv-pos k = toℕ-fromℕ< (mod-suc-bound (suc n ∸ toℕ k) n)

-- For k > 0 (toℕ k = suc k'), toℕ (inv-pos k) ≡ n ∸ toℕ k' (mod-suc-id kicks in).
