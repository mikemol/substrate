------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod.Reconstruction
--
-- The fundamental DivMod equation:
--
--   div-mod-eq : ∀ a b → a ≡ (a mod-suc b) ℕ+ (a div-suc b) * (suc b)
--
-- Mirrors stdlib's `m≡m%n+[m/n]*n`. Proof by induction on `a`,
-- dispatching on the same with-clause that defines _mod-suc_ and
-- _div-suc_. The NO branch (mod-suc wraps) uses Order.≤-tight to
-- conclude `a mod-suc b ≡ b`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.DivMod.Reconstruction where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Order using (≤-tight)
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Nat.Nat.DivSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Category.BWTEmergence

div-mod-eq : (a b : ℕ) → a ≡ (a mod-suc b) ℕ+ (a div-suc b) * (suc b)
div-mod-eq zero    _ = refl
div-mod-eq (suc a) b with suc (a mod-suc b) <? suc b | mod-suc-bound a b | div-mod-eq a b
... | yes _ | _      | ih = cong suc ih
... | no ¬p | bound  | ih =
  cong suc
    (trans ih
           (cong (_ℕ+ (a div-suc b) * suc b)
                 (≤-tight (a mod-suc b) b bound (λ p → ¬p (s≤s p)))))
