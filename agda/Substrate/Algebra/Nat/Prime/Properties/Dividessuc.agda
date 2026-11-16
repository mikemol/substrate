------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.Dividessuc
--
-- Defines: _∣suc?_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.Dividessuc where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Nat.Nat.DivSuc
open import Substrate.Algebra.Nat.DivMod.Reconstruction
open import Substrate.Algebra.Nat.DivMod.Unique.DivmodUnique
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Nat.Prime.Properties.Mod0ToDivides
open import Substrate.Algebra.Nat.Prime.Properties.DividesTomod0



_∣suc?_ : (d n : ℕ) → Dec (suc d ∣ n)
d ∣suc? n with (n mod-suc d) ≟ zero
... | yes eq  = yes (mod0→∣ n d eq)
... | no  ¬eq = no λ div → ¬eq (∣→mod0 n d div)
