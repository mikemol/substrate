------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosInvPos
--
-- Defines: toℕ-inv-pos-inv-pos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Nat.Properties.Sub
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosInvPos (n : ℕ) where

-- ⚑ `Cyclic.Inverse` DISSOLVED; `…InvInv.Private` provides ZERO names (Ⓐ¹²′).
-- ⚑ THIS IS THE INVOLUTION'S CORE: both Fin cases of `inv-pos ∘ inv-pos = id`,
-- composed from the zero/suc lemmas below it.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPos n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosSuc n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.ToNatInvPosZero n



toℕ-inv-pos-inv-pos : (k : Fin (suc n)) →
                      toℕ (inv-pos (inv-pos k)) ≡ toℕ k
toℕ-inv-pos-inv-pos zero =
  trans (toℕ-inv-pos (inv-pos zero))
  (cong-trans (λ x → (suc n ∸ x) mod-suc n) toℕ-inv-pos-zero
         (suc-mod-suc-self n))
toℕ-inv-pos-inv-pos (suc k') =
  trans (toℕ-inv-pos (inv-pos (suc k')))
  (cong-trans (λ x → (suc n ∸ x) mod-suc n) (toℕ-inv-pos-suc k')
  (cong-trans (_mod-suc n) (∸-suc-l n (n ∸ toℕ k') (∸-≤-self n (toℕ k')))
  (cong-trans (λ x → (suc x) mod-suc n) (∸-∸-cancel n (toℕ k') (<→≤ (toℕ-bound k')))
         (mod-suc-id (suc (toℕ k')) n (toℕ-bound (suc k'))))))
