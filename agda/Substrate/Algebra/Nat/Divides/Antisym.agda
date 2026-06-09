------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Antisym
--
-- Antisymmetry of divisibility:
--   ∣-antisym : a ∣ b → b ∣ a → a ≡ b
--
-- Pure multiplicative route (no order/≤): a = k'·b, b = k·a ⟹ a = (k'·k)·a;
-- for a = suc _ cancel a to force k'·k = 1, hence k = 1 (*≡1ʳ), hence b = a.
-- (Used by the Bézout/Euclid uniqueness route for ℚ.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Antisym where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-zeroʳ; *-identityˡ; *-assoc)
open import Substrate.Foundation.Nat.Properties.Cancel using (*-cancelʳ-suc)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Algebra.Nat.Divides.One using (*≡1ʳ)

∣-antisym : {a b : ℕ} → a ∣ b → b ∣ a → a ≡ b
∣-antisym {zero}   (divides k b≡k0) _                   = sym (trans b≡k0 (*-zeroʳ k))
∣-antisym {suc a′} {b} (divides k b≡ka) (divides k′ a≡k′b) = sym b≡a
  where
    a≡k′ka : suc a′ ≡ (k′ * k) * suc a′
    a≡k′ka = trans a≡k′b (trans (cong (k′ *_) b≡ka) (sym (*-assoc k′ k (suc a′))))
    k′k≡1 : k′ * k ≡ 1
    k′k≡1 = sym (*-cancelʳ-suc (suc zero) (k′ * k) a′
                  (trans (*-identityˡ (suc a′)) a≡k′ka))
    k≡1 : k ≡ 1
    k≡1 = *≡1ʳ k′ k k′k≡1
    b≡a : b ≡ suc a′
    b≡a = trans b≡ka (trans (cong (_* suc a′) k≡1) (*-identityˡ (suc a′)))
