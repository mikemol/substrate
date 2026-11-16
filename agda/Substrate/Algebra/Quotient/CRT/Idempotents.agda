------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.Idempotents
--
-- The CRT idempotent data (def module, proof-free per the def/proof
-- separation policy): the local solutions e₁,e₂ for moduli (suc m, suc n)
-- — e₁ ≡ 1 mod (suc m), ≡ 0 mod (suc n); e₂ the mirror. The combine map
-- + its correctness live in CRT.FromIdempotents.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.Idempotents where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Eq

record CRTIdempotents (m n : ℕ) : Set where
  field
    e₁ e₂    : ℕ
    e₁-mod-m : e₁ mod-suc m ≡ 1
    e₁-mod-n : e₁ mod-suc n ≡ 0
    e₂-mod-m : e₂ mod-suc m ≡ 0
    e₂-mod-n : e₂ mod-suc n ≡ 1
