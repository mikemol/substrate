------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtToNatId
--
-- Defines: fromℕ<-toℕ-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Inverse; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
module Substrate.Groups.Coxeter.Cyclic.Inverse.FromNatLtToNatId (n : ℕ) where

-- ⚑ `…Cyclic.Bridge n` DROPPED (Ⓑ2c-BRIDGE10″) — it was this file's ONLY import
-- and a pure conduit: the lemma quantifies its own `∀ {m}` and needs nothing from
-- the Cyclic telescope, only Fin/Nat/Eq, all now bound at their homes.
-- ⚑ THE `(n : ℕ)` TELESCOPE IS UNUSED HERE and kept only because consumers apply
-- it; that it survives a repair unread is a finding for a later pass, not this one.



------------------------------------------------------------------------
-- inv-canonical (Fin-indexed): bridged via the inv-power-eq lemma.
------------------------------------------------------------------------

fromℕ<-toℕ-id : ∀ {m} (k : Fin m) (p : toℕ k < m) → fromℕ< p ≡ k
fromℕ<-toℕ-id {suc _} zero    (s≤s _)   = refl
fromℕ<-toℕ-id {suc _} (suc k) (s≤s p')  = cong suc (fromℕ<-toℕ-id k p')
