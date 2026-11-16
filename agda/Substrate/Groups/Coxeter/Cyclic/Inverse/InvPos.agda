------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos
--
-- Defines: inv-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Inverse; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑⚑ THIS FILE HAD NO TELESCOPE AND APPLIED ONE ANYWAY (Ⓑ2c-BRIDGE10).  It read
-- `module … InvPos where` (no parameter) and then `open import …Cyclic.Bridge n`,
-- so `n` was unbound — and `Bridge` itself no longer exists, having been dissolved
-- into one leaf per theorem by the ban-decompose commit (771283c8).
--
-- ⚑ AND THE BARE `Bridge n` WAS CARRYING A WHOLE TRANSITIVE SURFACE.  The old
-- Bridge did `open import …Base n public`, so a consumer that named it inherited
-- `Fin`/`toℕ`/`fromℕ<`/`mod-suc-bound`/`_∸_` without ever importing them.  That is
-- the re-export hazard exactly: names whose home the consumer cannot see, and
-- when the conduit dissolved they vanished with it.  Bound at their real homes
-- here, which is what the ban asks for and what the sibling `InvPosAddMod`
-- already does.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf

module Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos (n : ℕ) where



------------------------------------------------------------------------
-- inv-pos: the inverse position via (suc n ∸ toℕ k) mod-suc n.
------------------------------------------------------------------------

inv-pos : Fin (suc n) → Fin (suc n)
inv-pos k = fromℕ< (mod-suc-bound (suc n ∸ toℕ k) n)
