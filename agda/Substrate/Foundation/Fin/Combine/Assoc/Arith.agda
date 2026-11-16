------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc.Arith
--
-- Defines: arith
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin.Combine.Assoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc.Arith where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 2. The arithmetic core: (A·n ℕ+ B)·p ℕ+ C = A·(n·p) ℕ+ (B·p ℕ+ C).
------------------------------------------------------------------------

arith : ∀ A n B p C → (A * n ℕ+ B) * p ℕ+ C ≡ A * (n * p) ℕ+ (B * p ℕ+ C)
arith A n B p C =
  trans (cong (_ℕ+ C) (*-distribʳ-+ p (A * n) B))
        (trans (+ℕ-assoc (A * n * p) (B * p) C)
               (cong (_ℕ+ (B * p ℕ+ C)) (*-assoc A n p)))
