------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.Private (n : ℕ) where

-- ⚑ `Cyclic.Inverse` dissolved into six leaves, each keeping the `(n : ℕ)`
-- telescope — so the applied argument carries over unchanged, once per leaf. Like
-- `S4-Composed`, this was an APPLIED import (`import … as .#<anon>`), invisible to
-- `rewire_to_leaves`, which is why both survived every earlier sweep.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvCanonical n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtToNatId n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtPowerToNat n




------------------------------------------------------------------------
-- 1. toℕ-inv-pos-inv-pos: the Fin-level involution at the toℕ image.
------------------------------------------------------------------------

-- toℕ (inv-pos k) ≡ (suc n ∸ toℕ k) mod-suc n.
