------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.DividesTomod0
--
-- Defines: ∣→mod0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.DividesTomod0 where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
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



------------------------------------------------------------------------
-- 2. Decidable divisibility: the converse (a divisor forces remainder 0, by
--    mod uniqueness), so `suc d ∣? n` decides via `n mod-suc d ≟ 0`.
------------------------------------------------------------------------

∣→mod0 : (n d : ℕ) → suc d ∣ n → n mod-suc d ≡ 0
∣→mod0 n d (divides q n≡q*sd) =
  sym (proj₂ (divmod-unique q (n div-suc d) zero (n mod-suc d) d
                (s≤s z≤n) (mod-suc-bound n d) eqn))
  where
    eqn : q * suc d ℕ+ zero ≡ (n div-suc d) * suc d ℕ+ (n mod-suc d)
    eqn = trans (+ℕ-identityʳ (q * suc d))
           (trans (sym n≡q*sd)
             (trans (div-mod-eq n d)
                    (+ℕ-comm (n mod-suc d) ((n div-suc d) * suc d))))
